from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Category, Product, Brand


@registry.register_document
class CategoryDocument(Document):
    id = fields.IntegerField(attr="id")
    name = fields.TextField(analyzer='russian')
    description = fields.TextField(analyzer='russian')

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


@registry.register_document
class ProductDocument(Document):
    id = fields.IntegerField(attr="id")
    title = fields.TextField(analyzer='russian')
    description = fields.TextField(analyzer='russian')
    article = fields.KeywordField()

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


@registry.register_document
class BrandDocument(Document):
    id = fields.IntegerField(attr="id")
    name = fields.TextField(analyzer='russian')

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
