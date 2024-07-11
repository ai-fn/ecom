from account.models import CustomUser
from api.serializers import ProductCatalogSerializer
from shop.models import FavoriteProduct, Product
from api.serializers import ActiveModelSerializer
from rest_framework import serializers


class FavoriteProductSerializer(ActiveModelSerializer):
    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), source="user")

    class Meta:
        model = FavoriteProduct
        fields = [
            "id",
            "user_id",
            "product",
            "product_id"
        ]
