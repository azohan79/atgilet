from django.contrib import admin
from .models import Menu, MenuItem, SettingsConfig


@admin.register(SettingsConfig)
class SettingsConfigAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode",)

    def has_add_permission(self, request):
        # Разрешаем создать только ОДНУ запись настроек
        if SettingsConfig.objects.exists():
            return False
        return super().has_add_permission(request)
    
@admin.register(SettingsConfig)
class SettingsConfigAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode",)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fk_name = "menu"
    fields = (
        "parent",
        "title",
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
    list_display = ("title", "menu", "parent", "order", "is_active")
    list_filter = ("menu", "is_active")
    search_fields = ("title", "url", "named_url")
    ordering = ("menu", "order")
