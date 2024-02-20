from rest_framework import viewsets

from account.models import City
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    """Возвращает города
    Args:
        viewsets (_type_): _description_
    """

    queryset = City.objects.all().order_by("-created_at")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAdminPermission]
