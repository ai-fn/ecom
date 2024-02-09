from rest_framework import serializers
from account.models import CityGroup

from api.serializers import CitySerializer


class CityGroupSerializer(serializers.ModelSerializer):
    main_city = CitySerializer(read_only=True)
    cities = CitySerializer(many=True, read_only=True)

    class Meta:
        model = CityGroup
        fields = [
            "id",
            "name",
            "main_city",
            "cities",
        ]
