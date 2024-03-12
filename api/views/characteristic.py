from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.characteristic import CharacteristicSerializer

from shop.models import Characteristic

from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=['Shop']
)
class CharacteristicViewSet(viewsets.ModelViewSet):
    """Возвращает характеристики продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = Characteristic.objects.all().order_by("-created_at")
    serializer_class = CharacteristicSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
