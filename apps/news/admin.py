from django.contrib import admin
from .models import NewsPost, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "category", "author_name")
    list_filter = ("is_published", "category", "published_at")
    search_fields = ("title", "excerpt", "content", "tags", "author_name")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at", "-created_at")
    fieldsets = (
        ("Main", {"fields": ("title", "slug", "excerpt", "content", "image")}),
        ("Meta", {"fields": ("author_name", "category", "tags")}),
        ("Publishing", {"fields": ("is_published", "published_at")}),
    )