from rest_framework import serializers

from account.models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "domain",
            "nominative_case",
            "genitive_case",
            "dative_case",
            "accusative_case",
            "instrumental_case",
            "prepositional_case",
        ]
