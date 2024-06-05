from rest_framework.serializers import ModelSerializer
from api.serializers import ProductCatalogSerializer
from shop.models import FavoriteProduct


class FavoriteProductSerializer(ModelSerializer):

    product = ProductCatalogSerializer()

    class Meta:
        model = FavoriteProduct
        exclude = [
            "created_at",
            "updated_at",
            "user",
        ]
