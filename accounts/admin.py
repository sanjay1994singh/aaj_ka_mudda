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
    list_editable = (
        "role",
        "is_verified",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )
    actions = (
        "approve_reporters",
        "remove_reporter_approval",
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

    @admin.action(description="Approve selected reporters")
    def approve_reporters(self, request, queryset):
        updated = queryset.filter(role="reporter").update(is_verified=True)
        self.message_user(request, f"{updated} reporter user(s) approved.")

    @admin.action(description="Remove reporter approval")
    def remove_reporter_approval(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} user approval(s) removed.")
