from django.contrib.sitemaps import Sitemap
from .models import News


class NewsSitemap(Sitemap):
    changefreq = "daily"

    priority = 0.9

    def items(self):
        return News.objects.all()

    def lastmod(self, obj):
        return obj.created_at
