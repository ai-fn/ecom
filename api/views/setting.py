from rest_framework import viewsets
from api.serializers.setting import SettingSerializer
from rest_framework.permissions import IsAdminUser

from shop.models import Setting

from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=['Settings']
)
class SettingViewSet(viewsets.ModelViewSet):
    """Возвращает настройки

    Args:
        viewsets (_type_): _description_
    """

    queryset = Setting.objects.all().order_by("-created_at")
    serializer_class = SettingSerializer
    permission_classes = [IsAdminUser]
