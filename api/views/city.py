from rest_framework import viewsets

from account.models import City
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city import CitySerializer

from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=['City']
)
class CityViewSet(viewsets.ModelViewSet):
    """Возвращает города
    Args:
        viewsets (_type_): _description_
    """

    queryset = City.objects.all().order_by("-created_at")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAdminPermission]
