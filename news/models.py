import re
from pathlib import Path

from django.db import models
from category.models import Category
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.utils import timezone


def hindi_slug(text):
    text = str(text).strip().lower()
    text = re.sub(r"[^\u0900-\u097Fa-zA-Z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def unique_news_slug(instance):
    base_slug = hindi_slug(instance.title)

    if not base_slug:
        base_slug = f"news-{NewsArticle.objects.count() + 1}"

    today = timezone.localdate().isoformat()
    max_base_length = instance._meta.get_field("slug").max_length - len(today) - 1
    base_slug = base_slug[:max_base_length].strip("-")
    slug = f"{today}-{base_slug}"
    counter = 1

    while NewsArticle.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        base_length = max_base_length - len(suffix)
        slug = f"{today}-{base_slug[:base_length].strip('-')}{suffix}"
        counter += 1

    return slug

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

    slug = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_news_slug(self)

        super().save(*args, **kwargs)

    @property
    def image_src(self):
        raw_path = ''
        if self.image:
            raw_path = self.image.name
        elif self.image_url:
            raw_path = self.image_url

        if not raw_path:
            return ''

        raw_path = str(raw_path).strip()
        if raw_path.startswith(('http://', 'https://')):
            return raw_path

        normalized_path = raw_path.lstrip('/')
        if normalized_path.startswith(('uploads/', 'media/')):
            return f'/{normalized_path}'

        return f'{settings.MEDIA_URL.rstrip("/")}/{normalized_path}'

    def local_image_path(self):
        raw_path = ''
        if self.image:
            raw_path = self.image.name
        elif self.image_url:
            raw_path = self.image_url

        if not raw_path or str(raw_path).startswith(('http://', 'https://')):
            return None

        normalized_path = str(raw_path).lstrip('/')
        if normalized_path.startswith('uploads/'):
            return Path(settings.BASE_DIR) / normalized_path
        if normalized_path.startswith('media/'):
            return Path(settings.BASE_DIR) / normalized_path
        return Path(settings.MEDIA_ROOT) / normalized_path

    def __str__(self):
        return self.title
