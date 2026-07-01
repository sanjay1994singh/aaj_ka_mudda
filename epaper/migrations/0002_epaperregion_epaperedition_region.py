from django.db import migrations, models
import django.db.models.deletion


INITIAL_REGIONS = [
    "Uttar Pradesh",
    "Delhi",
    "Bihar",
    "Himachal",
    "Haryana",
    "Jammu Kashmir",
]


def create_initial_regions(apps, schema_editor):
    EpaperRegion = apps.get_model("epaper", "EpaperRegion")
    for name in INITIAL_REGIONS:
        EpaperRegion.objects.get_or_create(name=name, defaults={"is_active": True})


def remove_initial_regions(apps, schema_editor):
    EpaperRegion = apps.get_model("epaper", "EpaperRegion")
    EpaperRegion.objects.filter(name__in=INITIAL_REGIONS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("epaper", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EpaperRegion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="epaperedition",
            name="region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="editions",
                to="epaper.epaperregion",
            ),
        ),
        migrations.RunPython(create_initial_regions, remove_initial_regions),
    ]
