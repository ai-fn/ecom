from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from api.serializers import ProductFileSerializer
from shop.models import ProductFile

from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=[
        "api"
    ]
)
class ProductFileViewSet(ModelViewSet):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Список файлов продукта",
        description="Получить список файлов продукта",
        responses={200: ProductFileSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Файл продукта",
        description="Получить информацию о конкретном файле продукта",
        responses={200: ProductFileSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создать файл продукта",
        description="Создать новый файл продукта",
        responses={201: ProductFileSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить файл продукта",
        description="Обновить информацию о файле продукта",
        responses={200: ProductFileSerializer()},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частично обновить файл продукта",
        description="Частично обновить информацию о файле продукта",
        responses={200: ProductFileSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить файл продукта",
        description="Удалить файл продукта",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
