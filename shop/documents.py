from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Category, Product, Review, Brand  # Import your models here


@registry.register_document
class CategoryDocument(Document):
    id = fields.IntegerField(attr="id")

    class Index:
        # Name of the Elasticsearch index
        name = "categories"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 1, "refresh_interval": "1s"}

    class Django:
        model = Category  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            "name",
            "slug",
            "is_visible",
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = False

        # Don't perform an index refresh after every update (for performance)
        auto_refresh = False


@registry.register_document
class ProductDocument(Document):
    id = fields.IntegerField(attr="id")
    category = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "slug": fields.TextField(),
        }
    )
    brand = fields.ObjectField(
        properties={
            "name": fields.TextField(),
        }
    )

    class Index:
        name = "products"
        settings = {"number_of_shards": 1, "number_of_replicas": 1, "refresh_interval": "1s"}

    class Django:
        model = Product
        fields = [
            "title",
            "description",
            "slug",
        ]


@registry.register_document
class ReviewDocument(Document):
    product = fields.ObjectField(
        properties={
            "title": fields.TextField(),
            "slug": fields.TextField(),
        }
    )
    user = fields.ObjectField(
        properties={
            "first_name": fields.TextField(),
            "last_name": fields.TextField(),
            "middle_name": fields.TextField(),
        }
    )

    class Index:
        name = "reviews"
        settings = {"number_of_shards": 2, "number_of_replicas": 1, "refresh_interval": "120s"}

    class Django:
        model = Review
        fields = [
            "rating",
            "review",
        ]


@registry.register_document
class BrandDocument(Document):

    class Index:
        name = "brands"
        settings = {"number_of_shards": 1, "number_of_replicas": 1, "refresh_interval": "1s"}

    class Django:
        model = Brand
        fields = [
            "name",
            "slug",
        ]
