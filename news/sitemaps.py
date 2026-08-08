from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from news.models import NewsArticle


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return [
            "home",
            "about_us",
            "contact_us",
            "privacy_policy",
            "disclaimer",
            "terms_and_conditions",
            "advertise_with_us",
            "editorial_policy",
        ]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return NewsArticle.objects.filter(status="published").order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("news_detail", kwargs={"slug": obj.slug})
