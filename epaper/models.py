from django.db import models


class EpaperRegion(models.Model):
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EpaperEdition(models.Model):
    region = models.ForeignKey(
        EpaperRegion,
        on_delete=models.PROTECT,
        related_name="editions",
    )
    section = models.CharField(max_length=80, default="Main")
    publish_date = models.DateField()
    pdf = models.FileField(upload_to="epaper/pdfs/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-publish_date", "-created_at"]
        unique_together = ("region", "section", "publish_date")

    @property
    def city(self):
        return self.region.name if self.region else "Aaj Ka Mudda"

    def __str__(self):
        return f"{self.city} - {self.section} - {self.publish_date:%d %b %Y}"


class EpaperPage(models.Model):
    edition = models.ForeignKey(EpaperEdition, related_name="pages", on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to="epaper/pages/")

    class Meta:
        ordering = ["number"]
        unique_together = ("edition", "number")

    def __str__(self):
        return f"{self.edition} page {self.number:02d}"
