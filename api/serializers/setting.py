from api.serializers import ActiveModelSerializer

from shop.models import Setting
from api.serializers import ActiveModelSerializer
from rest_framework import serializers


class SettingSerializer(ActiveModelSerializer):
    class Meta:
        model = Setting
        fields = [
            "id",
            "type",
            "value_string",
            "value_boolean",
            "value_number",
            "predefined_key",
            "custom_key",
        ]

    def validate(self, data):
        if not data.get("predefined_key") and not data.get("custom_key"):
            raise serializers.ValidationError(
                "Необходимо указать либо предопределенный ключ, либо пользовательский ключ."
            )
        if data.get("predefined_key") and data.get("custom_key"):
            raise serializers.ValidationError(
                "Укажите только один ключ: либо предопределенный, либо пользовательский."
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["value"] = instance.get_value()
        return representation

