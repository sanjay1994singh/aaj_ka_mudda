from django.db import migrations, models


def trim_slugs(apps, schema_editor):
    NewsArticle = apps.get_model("news", "NewsArticle")
    used_slugs = set()

    for article in NewsArticle.objects.order_by("id"):
        slug = (article.slug or f"news-{article.pk}")[:255].strip("-") or f"news-{article.pk}"
        base_slug = slug[:245].strip("-") or f"news-{article.pk}"
        counter = 1

        while slug in used_slugs or NewsArticle.objects.exclude(pk=article.pk).filter(slug=slug).exists():
            suffix = f"-{counter}"
            slug = f"{base_slug[:255 - len(suffix)].strip('-')}{suffix}"
            counter += 1

        if article.slug != slug:
            article.slug = slug
            article.save(update_fields=["slug"])
        used_slugs.add(slug)


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_newsarticle_slug_blank"),
    ]

    operations = [
        migrations.RunPython(trim_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="newsarticle",
            name="slug",
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
    ]
