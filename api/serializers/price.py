from rest_framework import serializers

from shop.models import Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = [
            "id",
            "product",
            "city_group",
            "price",
        ]
