import os
from django.db.models.base import Model
from django.contrib.sitemaps import Sitemap

from shop.models import Product, Category
from shop.utils import get_base_domain


class CustomSitemap:

    def __init__(self, domain=None) -> None:
        self.catalog_url = "katalog"
        self.base_domain = get_base_domain() + "/"
        if domain is not None:
            self.domain = domain
        
    def get_domain(self, site=None):
        if domain := getattr(self, "domain", None):
            return domain

        return self.base_domain

    def get_abs_path(self, link):
        return os.path.join(self.catalog_url, *link.split("/")[3:])


class ProductSitemap(CustomSitemap, Sitemap):
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
        return os.path.join(self.catalog_url, obj.category.slug, obj.slug)


class CategorySitemap(CustomSitemap, Sitemap):
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
    
    def location(self, obj):
        return obj.get_absolute_url()
