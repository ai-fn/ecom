from api.serializers import ActiveModelSerializer

from account.models import City
from api.serializers import SimpleCityGroupSerializer


class CitySerializer(ActiveModelSerializer):

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "domain",
            "city_group",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["city_group"] = SimpleCityGroupSerializer(instance.city_group).data if instance.city_group else None
        return data
