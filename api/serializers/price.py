from api.serializers import ActiveModelSerializer

from shop.models import Price

class PriceSerializer(ActiveModelSerializer):
    class Meta:
        model = Price
        fields = [
            "id",
            "product",
            "city_group",
            "price",
        ]
