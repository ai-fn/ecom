from rest_framework.serializers import ModelSerializer

from api.serializers.active_model import ActiveModelSerializer
from bitrix_app.models import Lead


class LeadSerializer(ActiveModelSerializer, ModelSerializer):
    
    class Meta:
        model = Lead
        fields = [
            "id",
            "bitrix_id",
            "title",
            "status",
        ]
