from django.db.models.base import Model
from django.shortcuts import redirect
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from shop.models import Product, Category


class CustomSitemap:

    def __init__(self, domain=None) -> None:
        self.base_domain = "krov.market/"
        if domain is not None:
            self.domain = domain
        
    def get_domain(self, site=None):
        if getattr(self, "domain", None):
            return f"{self.domain}.{self.base_domain}"
        
        return self.base_domain

    def get_abs_path(self, link):
        return "/".join(link.split("/")[3:])


# TODO занести в сайтмап урлы
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
        return self.get_abs_path(reverse("api:products-productdetail", args=[obj.pk]))


# TODO занести в сайтмап урлы
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
        return self.get_abs_path(reverse("api:shop:product_list_by_category", args=[obj.slug]))
