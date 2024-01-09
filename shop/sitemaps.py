from django.db.models.base import Model
from django.shortcuts import redirect
from blog.models import Article
from django.contrib.sitemaps import Sitemap

from shop.models import Product, Category


# TODO занести в сайтмап урлы
class ProductSitemap(Sitemap):
    """
    Карта-сайта для продуктов
    """

    changefreq = "always"

    priority = 0.8

    protocol = "https"

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj: Model) -> str:
        return redirect("home")


# TODO занести в сайтмап урлы
class CategorySitemap(Sitemap):
    """Карта сайта для категорий

    Args:
        Sitemap (_type_): _description_
    """

    changefreq = "monthly"

    priority = 0.9

    protocol = "https"

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
