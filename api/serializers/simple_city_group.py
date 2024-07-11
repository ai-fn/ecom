from api.serializers import ActiveModelSerializer

from account.models import CityGroup
from api.serializers import ActiveModelSerializer


class SimpleCityGroupSerializer(ActiveModelSerializer):

    class Meta:
        model = CityGroup
        fields = [
            "id",
            "name",
        ]
