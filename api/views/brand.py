from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.brand import BrandSerializer
from shop.models import Brand
from rest_framework import viewsets


class BrandView(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
