from rest_framework import viewsets
from api.filters import PriceFilter
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.price import PriceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from shop.models import Price


class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all().order_by("-created_at")
    serializer_class = PriceSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PriceFilter
