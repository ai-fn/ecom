from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField

from api.serializers.active_model import ActiveModelSerializer
from bitrix_app.services.bitrix_service import Bitrix24API
from bitrix_app.models import Lead




class LeadSerializer(ActiveModelSerializer, ModelSerializer):

    bitrix_id = IntegerField(read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "bitrix_id",
            "status",
            "title",
            "is_active",
            "dynamical_fields",
        ]

    def validate_dynamical_fields(self, value: dict):
        allowed_fields = Bitrix24API().get_allowed_fields()
        for key, _ in value.items():
            try:
                allowed_fields[key]
            except KeyError:
                raise ValidationError(f"'{key}' is not allow field for lead.")
        
        return value
