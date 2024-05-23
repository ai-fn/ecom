from rest_framework.serializers import ModelSerializer, SerializerMethodField
from shop.models import Characteristic


class CharacteristicFilterSerializer(ModelSerializer):
    
    values = SerializerMethodField()

    class Meta:
        model = Characteristic
        fields = ["name", "slug", "values"]
    
    def get_values(self, obj):
        return obj.characteristicvalue_set.values_list("value", flat=True)
