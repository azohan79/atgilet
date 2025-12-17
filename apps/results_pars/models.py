# apps/results_pars/models.py
from django.db import models
from django.utils import timezone


class TargetConfig(models.Model):
    is_active = models.BooleanField(default=True)
    target_team_name = models.CharField(max_length=255, default="AT Gilet")
    target_ffcv_team_id = models.CharField(max_length=64, blank=True, null=True)

    base_url = models.URLField(default="https://www.ffcv.es")
    team_matches_url_template = models.CharField(
        max_length=500,
        default="/equipo_p_partidos.php?id_equipo={team_id}",
    )
    calendar_url_template = models.CharField(max_length=500, blank=True, null=True)
    standings_url_template = models.CharField(max_length=500, blank=True, null=True)

    poll_interval_minutes = models.PositiveIntegerField(default=60)

    def clean(self):
        # Singleton enforcement (admin-level + model-level)
        if not self.pk and TargetConfig.objects.exists():
            raise ValueError("Only one TargetConfig record is allowed.")

    def save(self, *args, **kwargs):
        if not self.pk and TargetConfig.objects.exists():
            raise ValueError("Only one TargetConfig record is allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"TargetConfig(active={self.is_active}, team={self.target_team_name})"


class Team(models.Model):
    ffcv_team_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    shield_url = models.URLField(blank=True, null=True)
    is_target = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CompetitionContext(models.Model):
    name = models.CharField(max_length=255)
    season_name = models.CharField(max_length=255, blank=True, null=True)

    ffcv_temp_id = models.CharField(max_length=64, blank=True, null=True)
    ffcv_modalidad_id = models.CharField(max_length=64, blank=True, null=True)
    ffcv_competicion_id = models.CharField(max_length=64, blank=True, null=True)
    ffcv_torneo_id = models.CharField(max_length=64, blank=True, null=True)

    source_url = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.season_name or 'n/a'})"


class Round(models.Model):
    competition = models.ForeignKey(CompetitionContext, on_delete=models.CASCADE, related_name="rounds")
    round_number = models.PositiveIntegerField()
    round_date = models.DateField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["competition", "round_number"], name="uniq_round_competition_number")
        ]

    def __str__(self):
        return f"{self.competition}: Jornada {self.round_number}"


class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "SCHEDULED"
        PLAYED = "PLAYED", "PLAYED"
        POSTPONED = "POSTPONED", "POSTPONED"
        CANCELLED = "CANCELLED", "CANCELLED"
        UNKNOWN = "UNKNOWN", "UNKNOWN"

    competition = models.ForeignKey(CompetitionContext, on_delete=models.CASCADE, related_name="matches")
    round = models.ForeignKey(Round, on_delete=models.SET_NULL, related_name="matches", blank=True, null=True)

    kickoff_at = models.DateTimeField(blank=True, null=True)

    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="away_matches")

    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNKNOWN)
    result_note = models.CharField(max_length=50, blank=True, null=True)  # e.g. PEN

    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, blank=True, null=True)

    source_url = models.URLField()
    external_key = models.CharField(max_length=255, unique=True)

    is_target_match = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.home_team} - {self.away_team} ({self.kickoff_at})"


class StandingsSnapshot(models.Model):
    competition = models.ForeignKey(CompetitionContext, on_delete=models.CASCADE, related_name="standings_snapshots")
    round = models.ForeignKey(Round, on_delete=models.SET_NULL, blank=True, null=True)
    captured_at = models.DateTimeField(default=timezone.now)
    source_url = models.URLField()
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"Standings {self.competition} @ {self.captured_at:%Y-%m-%d %H:%M}"


class StandingsRow(models.Model):
    snapshot = models.ForeignKey(StandingsSnapshot, on_delete=models.CASCADE, related_name="rows")
    team = models.ForeignKey(Team, on_delete=models.PROTECT)

    position = models.PositiveIntegerField()
    played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_diff = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["snapshot", "team"], name="uniq_standings_row_snapshot_team")
        ]


class IngestionRun(models.Model):
    class RunStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "SUCCESS"
        ERROR = "ERROR", "ERROR"
        SKIPPED = "SKIPPED", "SKIPPED"

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=RunStatus.choices, default=RunStatus.SKIPPED)

    parsed_matches = models.PositiveIntegerField(default=0)
    updated_matches = models.PositiveIntegerField(default=0)

    errors = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"IngestionRun({self.status}) {self.started_at:%Y-%m-%d %H:%M}"
