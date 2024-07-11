from api.serializers import ActiveModelSerializer

from shop.models import Characteristic


class CharacteristicSerializer(ActiveModelSerializer):
    class Meta:
        model = Characteristic
        fields = [
            "id",
            "name",
            "category",
        ]
