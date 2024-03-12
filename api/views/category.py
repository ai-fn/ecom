from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.category import CategorySerializer
from api.serializers.category_detail import CategoryDetailSerializer
from django.shortcuts import get_object_or_404
from shop.models import Category
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=['Shop']
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return CategoryDetailSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], url_path="by-slug/(?P<slug>[^/.]+)")
    def retrieve_by_slug(self, request, slug=None):
        """
        Кастомное действие для получения категории по слагу.
        """
        category = get_object_or_404(Category, slug=slug)
        serializer = self.get_serializer(category)
        return Response(serializer.data)
