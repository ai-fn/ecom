from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.category_meta_data import CategoryMetaDataSerializer

from shop.models import CategoryMetaData

class CategoryMetaDataViewSet(viewsets.ModelViewSet):
    queryset = CategoryMetaData.objects.all().order_by("-created_at")
    serializer_class = CategoryMetaDataSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

