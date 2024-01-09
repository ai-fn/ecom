from django.db.models.base import Model
from django.shortcuts import redirect
from blog.models import Article
from django.contrib.sitemaps import Sitemap


class ArticleSitemap(Sitemap):

    """

    Карта-сайта для статей

    """

    changefreq = "monthly"

    priority = 0.9

    protocol = "https"

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj: Model) -> str:
        return redirect("home")
