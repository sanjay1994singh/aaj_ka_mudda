from django.db import models
from category.models import Category
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings

class NewsArticle(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="news"
    )

    title = models.CharField(
        max_length=500
    )

    slug = models.SlugField(
        max_length=700,
        unique=True,
        allow_unicode=True
    )

    keywords = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    short_description = models.TextField(
        blank=True,
        null=True
    )

    content = CKEditor5Field(
        "Content",
        config_name="default"
    )

    image = models.ImageField(
        upload_to="news/",
        blank=True,
        null=True
    )

    image_url = models.URLField(
        blank=True,
        null=True
    )

    image_description = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    views = models.PositiveIntegerField(
        default=0
    )

    is_breaking = models.BooleanField(
        default=False
    )

    is_featured = models.BooleanField(
        default=False
    )

    is_slider = models.BooleanField(
        default=False
    )

    is_recommended = models.BooleanField(
        default=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="published"
    )

    optional_url = models.URLField(blank=True, null=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
