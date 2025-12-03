from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode",)

    def has_add_permission(self, request):
        # Разрешаем создать только ОДНУ запись настроек
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)
