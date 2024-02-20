from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.characteristic_value import CharacteristicValueSerializer

from shop.models import CharacteristicValue

class CharacteristicValueViewSet(viewsets.ModelViewSet):
    """Возвращает значение характеристик продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = CharacteristicValue.objects.all().order_by("-created_at")
    serializer_class = CharacteristicValueSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
