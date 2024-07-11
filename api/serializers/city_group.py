from api.serializers import ActiveModelSerializer
from account.models import CityGroup

from api.serializers import CitySerializer


class CityGroupSerializer(ActiveModelSerializer):

    class Meta:
        model = CityGroup
        fields = [
            "id",
            "name",
            "main_city",
            "cities",
        ]
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)
        data["cities"] = CitySerializer(instance.cities.all(), many=True).data if instance.cities.exists() else None
        data["main_city"] = CitySerializer(instance.main_city).data if instance.main_city else None
        return data
