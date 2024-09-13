from django.db.models import Avg
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Category, Product, Brand


@registry.register_document
class CategoryDocument(Document):
    id = fields.IntegerField(attr="id")

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
        ]


@registry.register_document
class ProductDocument(Document):
    id = fields.IntegerField(attr="id")
    category = fields.ObjectField(
        properties={
            "slug": fields.TextField(analyzer='russian'),
            "name": fields.TextField(analyzer='russian'),
        }
    )
    price = fields.NestedField(
        properties={
            'price': fields.FloatField(),
            'old_price': fields.FloatField(),
            'domain': fields.TextField(analyzer='russian'),
            'in_promo': fields.BooleanField()
        }
    )
    rating = fields.FloatField()

    def prepare_rating(self, instanse):
        value = instanse.reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0.0
        return round(value, 1)

    def prepare_price(self, instance):
        """Метод для извлечения цен из связи M2M"""
        return [
            {
                "price": price.price,
                "old_price": price.old_price,
                "domain": price.city_group.main_city.domain,
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
