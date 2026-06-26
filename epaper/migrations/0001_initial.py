from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EpaperEdition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("city", models.CharField(default="Aaj Ka Mudda", max_length=120)),
                ("section", models.CharField(default="Main", max_length=80)),
                ("publish_date", models.DateField()),
                ("pdf", models.FileField(upload_to="epaper/pdfs/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-publish_date", "-created_at"],
                "unique_together": {("city", "section", "publish_date")},
            },
        ),
        migrations.CreateModel(
            name="EpaperPage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveIntegerField()),
                ("image", models.ImageField(upload_to="epaper/pages/")),
                (
                    "edition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pages",
                        to="epaper.epaperedition",
                    ),
                ),
            ],
            options={
                "ordering": ["number"],
                "unique_together": {("edition", "number")},
            },
        ),
    ]
