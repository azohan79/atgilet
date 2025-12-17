from django.contrib import admin
from .models import SettingsConfig, Menu, MenuItem


@admin.register(SettingsConfig)
class SettingsConfigAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode",)

    # если нужна только одна запись настроек
    def has_add_permission(self, request):
        if SettingsConfig.objects.exists():
            return False
        return super().has_add_permission(request)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fk_name = "menu"
    fields = (
        "parent",
        "title_es",
        "title_val",
        "title_en",
        "named_url",
        "url",
        "icon_class",
        "css_class",
        "html_attributes",
        "open_in_new_tab",
        "order",
        "is_active",
    )
    ordering = ("order",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active")
    list_filter = ("location", "is_active")
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("title_es", "menu", "parent", "order", "is_active")
    list_filter = ("menu", "is_active")
    search_fields = ("title_es", "title_val", "title_en", "url", "named_url")
    ordering = ("menu", "order")
