from django.http import Http404
from rest_framework import viewsets

from account.models import City
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import PromoSerializer
from shop.models import Promo
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["Shop"],
    parameters=[
        OpenApiParameter(
            name="domain",
            description="Домен города",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        )
    ],
    responses={200: PromoSerializer(many=True)},
    description="Retrieves promotions filtered by the domain of the city.",
)
class PromoViewSet(viewsets.ModelViewSet):
    serializer_class = PromoSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_queryset(self):
        # Получаем домен из параметров запроса
        domain = self.request.query_params.get("domain")
        if not domain:
            raise Http404("Domain parameter is required to filter promotions.")

        # Находим города, соответствующие этому домену
        cities = City.objects.filter(domain=domain)
        if not cities.exists():
            raise Http404("No city found with the given domain.")

        # Возвращаем промоакции, связанные с найденными городами
        return Promo.objects.filter(cities__in=cities).distinct()
