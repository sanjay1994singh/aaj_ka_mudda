from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("editor", "Editor"),
        ("reporter", "Reporter"),
        ("user", "User"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user"
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        upload_to="users/avatar/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
