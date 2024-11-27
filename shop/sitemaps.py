import os
from django.db.models import Model
from django.contrib.sitemaps import Sitemap
from shop.models import Product, Category
from shop.utils import get_base_domain


class CustomSitemap:
    """
    Базовый класс для создания карты сайта, предоставляющий общую функциональность.
    """

    def __init__(self, domain: str = None) -> None:
        """
        Инициализация базового домена и каталога.

        :param domain: Домен сайта.
        """
        self.catalog_url = "katalog"
        self.base_domain = get_base_domain().strip("/") + "/"
        self.domain = domain if domain is not None else None

    def get_domain(self, site=None) -> str:
        """
        Получает текущий домен, учитывая город.

        :param site: Дополнительные данные о сайте (не используются).
        :return: Полный URL домена.
        """
        domain = self.base_domain
        if city_domain := getattr(self, "domain", None):
            domain = city_domain

        return f"{domain.strip('/')}/"

    def get_abs_path(self, link: str) -> str:
        """
        Генерирует абсолютный путь для переданной ссылки.

        :param link: Внутренняя ссылка.
        :return: Абсолютный путь.
        """
        return os.path.join(self.catalog_url, *link.split("/")[3:])


class ProductSitemap(CustomSitemap, Sitemap):
    """
    Карта сайта для продуктов.
    """

    changefreq = "always"
    priority = 0.8
    protocol = "https"

    def items(self):
        """
        Возвращает список всех продуктов для карты сайта.

        :return: QuerySet продуктов.
        """
        return Product.objects.all()

    def lastmod(self, obj: Product):
        """
        Возвращает дату последнего обновления объекта.

        :param obj: Объект продукта.
        :return: Дата последнего изменения.
        """
        return obj.updated_at

    def location(self, obj: Model) -> str:
        """
        Генерирует путь для продукта.

        :param obj: Объект продукта.
        :return: URL продукта.
        """
        return os.path.join(self.catalog_url, obj.category.slug, obj.slug)


class CategorySitemap(CustomSitemap, Sitemap):
    """
    Карта сайта для категорий.
    """

    changefreq = "monthly"
    priority = 0.9
    protocol = "https"

    def items(self):
        """
        Возвращает список всех категорий для карты сайта.

        :return: QuerySet категорий.
        """
        return Category.objects.all()

    def lastmod(self, obj: Category):
        """
        Возвращает дату последнего обновления объекта.

        :param obj: Объект категории.
        :return: Дата последнего изменения.
        """
        return obj.updated_at

    def location(self, obj: Model) -> str:
        """
        Возвращает абсолютный URL категории.

        :param obj: Объект категории.
        :return: URL категории.
        """
        return obj.get_absolute_url()
