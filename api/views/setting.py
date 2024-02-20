from rest_framework import viewsets
from api.serializers.setting import SettingSerializer
from rest_framework.permissions import IsAdminUser

from shop.models import Setting

class SettingViewSet(viewsets.ModelViewSet):
    """Возвращает настройки

    Args:
        viewsets (_type_): _description_
    """

    queryset = Setting.objects.all().order_by("-created_at")
    serializer_class = SettingSerializer
    permission_classes = [IsAdminUser]
