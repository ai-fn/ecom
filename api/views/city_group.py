from rest_framework import viewsets

from account.models import CityGroup
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city_group import CityGroupSerializer

class CityGroupViewSet(viewsets.ModelViewSet):
    """Возвращает группы городов

    Args:
        viewsets (_type_): _description_
    """

    queryset = CityGroup.objects.all().order_by("-created_at")
    serializer_class = CityGroupSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

