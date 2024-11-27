from django.db.models import Avg
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Category, Product, Brand


@registry.register_document
class CategoryDocument(Document):
    """
    Elasticsearch документ для индексации категорий.
    """

    id = fields.IntegerField(attr="id")
    products_exist = fields.BooleanField()

    class Index:
        name = "categories"
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "refresh_interval": "100s",
            "index.codec": "best_compression",
        }

    class Django:
        model = Category
        ignore_signals = False
        auto_refresh = False
        fields = [
            "name",
            "description",
            "slug",
            "is_active",
            "is_visible",
        ]

    def prepare_products_exist(self, instance: Category) -> bool:
        """
        Проверяет наличие активных товаров с ценами в категории.

        :param instance: Экземпляр категории.
        :return: True, если товары существуют, иначе False.
        """
        return instance.products.filter(
            is_active=True,
            prices__isnull=False,
        ).exists()


@registry.register_document
class ProductDocument(Document):
    """
    Elasticsearch документ для индексации товаров.
    """

    id = fields.IntegerField(attr="id")
    category = fields.ObjectField(
        properties={
            "slug": fields.TextField(analyzer="russian"),
            "name": fields.TextField(analyzer="russian"),
        }
    )
    prices = fields.ListField(
        fields.ObjectField(
            properties={
                "amount": fields.FloatField(),
                "cg_domain": fields.TextField(analyzer="russian"),
            }
        )
    )
    rating = fields.FloatField()

    def prepare_rating(self, instance: Product) -> float:
        """
        Подготовка рейтинга для индексации.

        :param instance: Экземпляр продукта.
        :return: Округленный средний рейтинг.
        """
        value = (
            instance.reviews.aggregate(average_rating=Avg("rating"))["average_rating"]
            or 0.0
        )
        return round(value, 1)

    def prepare_prices(self, instance: Product) -> list[dict]:
        """
        Подготовка цен для индексации.

        :param instance: Экземпляр продукта.
        :return: Список словарей с ценами.
        """
        return [
            {
                "amount": price.price,
                "cg_domain": price.city_group.main_city.domain,
            }
            for price in instance.prices.all().select_related("city_group__main_city")
        ]

    class Index:
        name = "products"
        settings = {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "refresh_interval": "120s",
            "index.codec": "best_compression",
        }

    class Django:
        model = Product
        fields = [
            "title",
            "description",
            "article",
            "in_stock",
            "is_new",
            "is_popular",
            "priority",
            "slug",
            "is_active",
        ]


@registry.register_document
class BrandDocument(Document):
    """
    Elasticsearch документ для индексации брендов.
    """

    id = fields.IntegerField(attr="id")

    class Index:
        name = "brands"
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "refresh_interval": "120s",
            "index.codec": "best_compression",
        }

    class Django:
        model = Brand
        fields = [
            "name",
            "slug",
            "is_active",
        ]
