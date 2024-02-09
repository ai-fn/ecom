from rest_framework import serializers

from shop.models import Setting

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            "id",
            "key",
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

