from django.contrib import admin
from .models import HomePage, HomeSliderSlide, HomeStatItem


class HomeSliderSlideInline(admin.TabularInline):
    model = HomeSliderSlide
    extra = 0
    fields = ("order", "is_active", "hero_image", "title_part1", "title_part2", "subtitle", "btn1_text", "btn1_url", "btn2_text", "btn2_url")
    ordering = ("order",)


class HomeStatItemInline(admin.TabularInline):
    model = HomeStatItem
    extra = 0
    fields = ("order", "value", "label")
    ordering = ("order",)


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    inlines = [HomeSliderSlideInline, HomeStatItemInline]
    list_display = ("id", "title")

    fieldsets = (
        ("Общее", {"fields": ("title",)}),

        ("Блок 1 — Слайдер (общие тексты/кнопки по умолчанию)", {
            "fields": (
                "hero_title_part1", "hero_title_part2", "hero_subtitle",
                "hero_btn1_text", "hero_btn1_url",
                "hero_btn2_text", "hero_btn2_url",
            )
        }),

        ("Блок 2 — О клубе", {
            "fields": ("about_vertical_title", "about_title", "about_text", "about_btn_text", "about_btn_url")
        }),

        ("Блок 3 — Анонс игры", {
            "fields": (
                "match_title", "match_text",
                "match_btn1_text", "match_btn1_url",
                "match_btn2_text", "match_btn2_url",
            )
        }),

        ("Блок 4 — Последние результаты (пока статично)", {
            "fields": ("results_vertical_title", "results_btn_text", "results_btn_url")
        }),

        ("Блок 7 — Видео", {
            "fields": ("video_title", "video_iframe_url", "video_poster")
        }),

        ("Блок 8 — Топ/категории (пока статично)", {
            "fields": ("top_vertical_title", "top_title", "top_text", "top_btn_text", "top_btn_url")
        }),

        ("Блок 9 — Турнирная таблица (динамика позже)", {
            "fields": ("table_title", "table_btn_text", "table_btn_url")
        }),

        ("Блок 10 — Новости (динамика позже)", {
            "fields": ("news_btn_text", "news_btn_url")
        }),
    )
