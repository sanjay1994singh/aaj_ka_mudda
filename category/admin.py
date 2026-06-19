from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "show_at_homepage",
        "show_on_menu",
        "color",
        "created_at",
    )
    list_filter = (
        "show_at_homepage",
        "show_on_menu",
        "created_at",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
