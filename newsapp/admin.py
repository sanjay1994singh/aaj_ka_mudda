from django.contrib import admin
from .models import Category, News, State

admin.site.site_header = "News Portal Admin"

admin.site.register(State)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title','views', 'category', 'is_breaking', 'created_at']

    search_fields = ['title']

    prepopulated_fields = {'slug': ('title',)}
