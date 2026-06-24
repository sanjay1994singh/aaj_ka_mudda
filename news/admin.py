from django.contrib import admin
from django.template.defaultfilters import truncatewords

from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = (
        "short_title",
        "category",
        "status",
        "author",
        "views",
        "created_at",
    )
    list_display_links = (
        "short_title",
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
    autocomplete_fields = (
        "category",
        "author",
    )
    readonly_fields = (
        "slug",
        "views",
        "updated_at",
    )
    list_per_page = 25
    list_select_related = (
        "category",
        "author",
    )

    @admin.display(description="Title", ordering="title")
    def short_title(self, obj):
        return truncatewords(obj.title, 10)
