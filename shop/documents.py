from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Category, Product, Review, Brand  # Import your models here


@registry.register_document
class CategoryDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = "categories"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

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
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

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

    class Index:
        name = "reviews"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Review
        fields = [
            "name",
            "rating",
            "review",
        ]


# You can add more Document classes for other models in a similar fashion.
