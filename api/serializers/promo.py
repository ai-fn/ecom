from rest_framework import serializers

from shop.models import Promo


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = [
            "id",
            "name",
            "category",
            "product",
            "image",
            "cities",
            "active_to",
        ]
