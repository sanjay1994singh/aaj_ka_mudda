from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_verified",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "is_verified",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "role",
                    "phone",
                    "avatar",
                    "bio",
                    "facebook_url",
                    "twitter_url",
                    "instagram_url",
                    "youtube_url",
                    "google_avatar_url",
                    "is_verified",
                )
            },
        ),
    )
