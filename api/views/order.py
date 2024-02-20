from rest_framework import viewsets
from api.serializers.order import OrderSerializer
from rest_framework.permissions import IsAuthenticated

from cart.models import Order


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
