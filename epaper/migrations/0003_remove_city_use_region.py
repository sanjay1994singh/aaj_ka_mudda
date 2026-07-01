from django.db import migrations, models
import django.db.models.deletion


def move_city_to_region(apps, schema_editor):
    EpaperEdition = apps.get_model("epaper", "EpaperEdition")
    EpaperRegion = apps.get_model("epaper", "EpaperRegion")

    for edition in EpaperEdition.objects.all().order_by("id"):
        if edition.region_id:
            continue

        region_name = (edition.city or "").strip() or "Aaj Ka Mudda"
        region, _ = EpaperRegion.objects.get_or_create(
            name=region_name,
            defaults={"is_active": True},
        )
        edition.region_id = region.pk
        edition.save(update_fields=["region"])


def reverse_region_to_city(apps, schema_editor):
    EpaperEdition = apps.get_model("epaper", "EpaperEdition")
    for edition in EpaperEdition.objects.select_related("region"):
        if edition.region:
            edition.city = edition.region.name
            edition.save(update_fields=["city"])


class Migration(migrations.Migration):

    dependencies = [
        ("epaper", "0002_epaperregion_epaperedition_region"),
    ]

    operations = [
        migrations.RunPython(move_city_to_region, reverse_region_to_city),
        migrations.AlterUniqueTogether(
            name="epaperedition",
            unique_together={("region", "section", "publish_date")},
        ),
        migrations.AlterField(
            model_name="epaperedition",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="editions",
                to="epaper.epaperregion",
            ),
        ),
        migrations.RemoveField(
            model_name="epaperedition",
            name="city",
        ),
    ]
