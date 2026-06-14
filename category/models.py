from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    color = models.CharField(
        max_length=20,
        default="#2d65fe"
    )

    show_at_homepage = models.BooleanField(
        default=True
    )

    show_on_menu = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "category_detail",
            kwargs={
                "slug": self.slug
            }
        )