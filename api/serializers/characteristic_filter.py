from api.serializers import ActiveModelSerializer
from shop.models import Characteristic
from rest_framework.serializers import SerializerMethodField


class CharacteristicFilterSerializer(ActiveModelSerializer):
    
    values = SerializerMethodField()

    class Meta:
        model = Characteristic
        fields = ["name", "slug", "values"]
    
    def get_values(self, obj):
        return obj.characteristicvalue_set.values("value", "slug").distinct()
