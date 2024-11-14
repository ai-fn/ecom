from rest_framework.serializers import ModelSerializer, SerializerMethodField, DecimalField
from cart.models import PickupPoint



class PickupPointDetailSerializer(ModelSerializer):
    coord_x = DecimalField(max_digits=9, decimal_places=6, coerce_to_string=False)
    coord_y = DecimalField(max_digits=9, decimal_places=6, coerce_to_string=False)

    class Meta:
        model = PickupPoint
        fields = "__all__"


class PickupPointSerializer(ModelSerializer):
    coordinate = SerializerMethodField()
    class Meta:
        model = PickupPoint
        fields = [
            "id",
            "address",
            "coordinate",
        ]

    def get_coordinate(self, obj) -> list:
        return [float(obj.coord_x), float(obj.coord_y)]
