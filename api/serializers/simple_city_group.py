from rest_framework import serializers

from account.models import CityGroup


class SimpleCityGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityGroup
        fields = [
            "id",
            "name",
        ]
