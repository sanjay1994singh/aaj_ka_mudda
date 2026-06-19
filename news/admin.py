from django.contrib import admin

from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "author",
        "is_breaking",
        "is_featured",
        "is_slider",
        "is_recommended",
        "views",
        "created_at",
    )
    list_filter = (
        "status",
        "category",
        "is_breaking",
        "is_featured",
        "is_slider",
        "is_recommended",
        "created_at",
    )
    search_fields = (
        "title",
        "keywords",
        "short_description",
        "content",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    autocomplete_fields = (
        "category",
        "author",
    )
    readonly_fields = (
        "views",
        "updated_at",
    )
