from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.category import CategorySerializer
from api.serializers.category_detail import CategoryDetailSerializer
from django.shortcuts import get_object_or_404
from shop.models import Category
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiExample


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
    
    @extend_schema(
        description="Получить список всех категорий",
        summary="Список категорий",
        responses={200: CategorySerializer(many=True)},
        examples=[
            OpenApiExample(
                name='List Response Example',
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Category A",
                        "slug": "category-a",
                        "order": 1,
                        "parent": None,
                        "children": None,
                        "parents": [
                            "Деке",
                            "deke-1"
                        ],
                        "category_meta": [],
                        "category_meta_id": None,
                        "icon": None,
                        "image_url": None,
                        "is_visible": True
                    },
                ],
                description="Пример ответа для получения списка всех категорий в Swagger UI",
                summary="Пример ответа для получения списка всех категорий",
                media_type="application/json",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Получить информацию о конкретной категории",
        summary="Информация о категории",
        responses={200: CategorySerializer()},
        examples=[
            OpenApiExample(
                name='Retrieve Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "Category A",
                    "slug": "category-a",
                    "order": 1,
                    "parent": None,
                    "children": None,
                    "parents": [
                        "Деке",
                        "deke-1"
                    ],
                    "category_meta": [],
                    "category_meta_id": None,
                    "icon": None,
                    "image_url": None,
                    "is_visible": True
                },
                description="Пример ответа для получения информации о конкретной категории в Swagger UI",
                summary="Пример ответа для получения информации о конкретной категории",
                media_type="application/json",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Создать новую категорию",
        summary="Создание категории",
        request=CategorySerializer,
        responses={201: CategorySerializer()},
        examples=[
            OpenApiExample(
                name='Create Request Example',
                request_only=True,
                value={
                    "name": "Category A",
                    "slug": "category-a",
                    "order": 1,
                    "parent": None,
                    "children": None,
                    "parents": [
                        "Деке",
                        "deke-1"
                    ],
                    "category_meta": [],
                    "category_meta_id": None,
                    "icon": None,
                    "image_url": None,
                    "is_visible": True
                },
                description="Пример запроса на создание новой категории в Swagger UI",
                summary="Пример запроса на создание новой категории",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Create Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "Category A",
                    "slug": "category-a",
                    "order": 1,
                    "parent": None,
                    "children": None,
                    "parents": [
                        "Деке",
                        "deke-1"
                    ],
                    "category_meta": [],
                    "category_meta_id": None,
                    "icon": None,
                    "image_url": None,
                    "is_visible": True
                },
                description="Пример ответа на создание новой категории в Swagger UI",
                summary="Пример ответа на создание новой категории",
                media_type="application/json",
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Обновить информацию о категории",
        summary="Обновление категории",
        request=CategorySerializer,
        responses={200: CategorySerializer()},
        examples=[
            OpenApiExample(
                name='Update Request Example',
                request_only=True,
                value={
                    "name": "New Name For Category A",
                    "slug": "new-name-for-category-a",
                    "order": 1,
                    "parent": None,
                    "children": None,
                    "parents": [
                                "Деке",
                                "deke-1"
                            ],
                    "category_meta": [],
                    "category_meta_id": None,
                    "icon": None,
                    "image_url": None,
                    "is_visible": True
                },
                description="Пример запроса на обновление информации о категории в Swagger UI",
                summary="Пример запроса на обновление информации о категории",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "New Name For Category A",
                    "slug": "new-name-for-category-a",
                    "order": 1,
                    "parent": None,
                    "children": None,
                    "parents": [
                        "Деке",
                        "deke-1"
                    ],
                    "category_meta": [],
                    "category_meta_id": None,
                    "icon": None,
                    "image_url": None,
                    "is_visible": True
                },
                description="Пример ответа на обновление информации о категории в Swagger UI",
                summary="Пример ответа на обновление информации о категории",
                media_type="application/json",
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Частично обновить информацию о категории",
        summary="Частичное обновление категории",
        request=CategorySerializer,
        responses={200: CategorySerializer()},
        examples=[
            OpenApiExample(
                name='Partial Update Request Example',
                request_only=True,
                value={
                    "name": "Updated Category Name"
                },
                description="Пример запроса на частичное обновление информации о категории в Swagger UI",
                summary="Пример запроса на частичное обновление информации о категории",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Partial Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "Updated Category Name",
                    "slug": "updated-category-name",
                    "order": 1,
                    "parent": None,
                    "children": None,
                    "parents": [
                        "Деке",
                        "deke-1"
                    ],
                    "category_meta": [],
                    "category_meta_id": None,
                    "icon": None,
                    "image_url": None,
                    "is_visible": True
                },
                description="Пример ответа на частичное обновление информации о категории в Swagger UI",
                summary="Пример ответа на частичное обновление информации о категории",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Удалить категорию",
        summary="Удаление категории",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Получение категории по слагу"
    )
    @action(detail=False, methods=["get"], url_path="by-slug/(?P<slug>[^/.]+)")
    def retrieve_by_slug(self, request, slug=None):
        """
        Кастомное действие для получения категории по слагу.
        """
        category = get_object_or_404(Category, slug=slug)
        serializer = self.get_serializer(category)
        return Response(serializer.data)
