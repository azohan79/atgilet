# apps/results_pars/management/commands/parse_ffcv_results.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from results_pars.models import (
    TargetConfig, Team, CompetitionContext, Round, Venue, Match, IngestionRun
)
from results_pars.services.ffcv_parser import FFCVParser


class Command(BaseCommand):
    help = "Parse FFCV schedules/results for AT Gilet only and upsert into DB."

    def handle(self, *args, **options):
        run = IngestionRun.objects.create(status=IngestionRun.RunStatus.SKIPPED, started_at=timezone.now())
        try:
            cfg = TargetConfig.objects.first()
            if not cfg or not cfg.is_active:
                run.status = IngestionRun.RunStatus.SKIPPED
                run.errors = "TargetConfig missing or inactive."
                return

            if not cfg.target_ffcv_team_id:
                run.status = IngestionRun.RunStatus.ERROR
                run.errors = "TargetConfig.target_ffcv_team_id is empty."
                return

            parser = FFCVParser(
                base_url=cfg.base_url,
                team_matches_url_template=cfg.team_matches_url_template,
                target_team_id=str(cfg.target_ffcv_team_id),
                target_team_name=cfg.target_team_name,
            )

            parsed = parser.parse_team_matches()

            parsed_count = 0
            updated_count = 0

            with transaction.atomic():
                # Ensure target team exists (ffcv id from config)
                target_team, _ = Team.objects.get_or_create(
                    ffcv_team_id=str(cfg.target_ffcv_team_id),
                    defaults={"name": cfg.target_team_name, "is_target": True},
                )
                if not target_team.is_target:
                    target_team.is_target = True
                    target_team.save(update_fields=["is_target"])

                for pm in parsed:
                    parsed_count += 1

                    # competition
                    comp, _ = CompetitionContext.objects.get_or_create(
                        name=pm.competition_name,
                        season_name=pm.season_name,
                        defaults={"source_url": pm.source_url, "is_active": True},
                    )

                    # round
                    rnd = None
                    if pm.round_number is not None:
                        rnd, _ = Round.objects.get_or_create(
                            competition=comp,
                            round_number=pm.round_number,
                            defaults={"round_date": pm.kickoff_at.date() if pm.kickoff_at else None},
                        )

                    # teams (opponent auto)
                    home_team = target_team if pm.home_name.lower().find(cfg.target_team_name.lower()) >= 0 else None
                    away_team = target_team if pm.away_name.lower().find(cfg.target_team_name.lower()) >= 0 else None

                    if home_team is None:
                        home_team, _ = Team.objects.get_or_create(
                            ffcv_team_id=f"auto:{pm.home_name}",
                            defaults={"name": pm.home_name, "is_target": False},
                        )
                    else:
                        home_team.name = pm.home_name
                        home_team.save(update_fields=["name"])

                    if away_team is None:
                        away_team, _ = Team.objects.get_or_create(
                            ffcv_team_id=f"auto:{pm.away_name}",
                            defaults={"name": pm.away_name, "is_target": False},
                        )
                    else:
                        away_team.name = pm.away_name
                        away_team.save(update_fields=["name"])

                    venue = None
                    if pm.venue_name:
                        venue, _ = Venue.objects.get_or_create(name=pm.venue_name)

                    obj, created = Match.objects.update_or_create(
                        external_key=pm.external_key,
                        defaults={
                            "competition": comp,
                            "round": rnd,
                            "kickoff_at": pm.kickoff_at,
                            "home_team": home_team,
                            "away_team": away_team,
                            "home_score": pm.home_score,
                            "away_score": pm.away_score,
                            "status": pm.status,
                            "result_note": pm.result_note,
                            "venue": venue,
                            "source_url": pm.source_url,
                            "is_target_match": True,
                        },
                    )
                    if not created:
                        updated_count += 1

            run.status = IngestionRun.RunStatus.SUCCESS
            run.parsed_matches = parsed_count
            run.updated_matches = updated_count

        except Exception as e:
            run.status = IngestionRun.RunStatus.ERROR
            run.errors = f"{type(e).__name__}: {e}"
            raise
        finally:
            run.finished_at = timezone.now()
            run.save()
