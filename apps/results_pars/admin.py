# apps/results_pars/admin.py
from django.contrib import admin
from .models import (
    TargetConfig, Team, CompetitionContext, Round, Venue, Match,
    StandingsSnapshot, StandingsRow, IngestionRun
)


@admin.register(TargetConfig)
class TargetConfigAdmin(admin.ModelAdmin):
    list_display = ("is_active", "target_team_name", "target_ffcv_team_id", "poll_interval_minutes")
    def has_add_permission(self, request):
        return not TargetConfig.objects.exists()


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "ffcv_team_id", "is_target")
    list_filter = ("is_target",)
    search_fields = ("name", "ffcv_team_id")


@admin.register(CompetitionContext)
class CompetitionContextAdmin(admin.ModelAdmin):
    list_display = ("name", "season_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "season_name")


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("competition", "round_number", "round_date")
    list_filter = ("competition",)
    search_fields = ("competition__name",)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name", "address")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("kickoff_at", "competition", "home_team", "away_team", "home_score", "away_score", "status", "is_target_match")
    list_filter = ("competition", "status", "is_target_match")
    search_fields = ("home_team__name", "away_team__name", "external_key")


class StandingsRowInline(admin.TabularInline):
    model = StandingsRow
    extra = 0


@admin.register(StandingsSnapshot)
class StandingsSnapshotAdmin(admin.ModelAdmin):
    list_display = ("competition", "round", "captured_at", "is_current")
    list_filter = ("competition", "is_current")
    inlines = [StandingsRowInline]


@admin.register(IngestionRun)
class IngestionRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "finished_at", "status", "parsed_matches", "updated_matches")
    readonly_fields = ("started_at", "finished_at", "status", "parsed_matches", "updated_matches", "errors")

    def has_add_permission(self, request):
        return False
