from rest_framework import viewsets
from api.serializers.products_in_order import ProductsInOrderSerializer
from rest_framework.permissions import IsAuthenticated
from cart.models import ProductsInOrder


class ProductsInOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductsInOrder.objects.all().order_by("-created_at")
    serializer_class = ProductsInOrderSerializer
    permission_classes = [IsAuthenticated]
