from rest_framework.serializers import ModelSerializer

from shop.models import ProductGroup


class ProductGroupSerializer(ModelSerializer):
    
    class Meta:
        model = ProductGroup
        exclude = ["updated_at", "created_at"]
