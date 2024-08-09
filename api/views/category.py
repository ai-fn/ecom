from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.category import CategorySerializer
from api.serializers.category_detail import CategoryDetailSerializer
from django.shortcuts import get_object_or_404
from shop.models import Category
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)


REQUEST_EXAMPLE = {
    "name": "Гидро-ветрозащита и пароизоляция",
    "slug": "gidro-vetrozashchita-i-paroizoliatsiia",
    "h1_tag": "dummy_h1_tag",
    "order": 2333,
    "parent": 2348,
    "children": [
        {
            "id": 2348,
            "name": "Армирующая ткань АЛЬФА ПЭЙСТ",
            "h1_tag": "dummy_h1_tag",
            "slug": "armiruiushchaia-tkan-al-fa-peist",
            "order": 2348,
            "parent": 2333,
            "children": [],
            "parents": [
                [
                    "Гидро-ветрозащита и пароизоляция",
                    "gidro-vetrozashchita-i-paroizoliatsiia",
                ]
            ],
            "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
            "image_url": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
            "is_visible": True,
            "is_popular": False,
            "thumb_img": "base64string",
            "is_acitve": True,
        },
    ],
    "parents": [],
    "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "image_url": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "is_visible": True,
    "is_popular": True,
    "thumb_img": "base64string",
    "is_acitve": True,
}
PARTIAL_UPDATE_REQUEST_EXAMPLE = {"name": REQUEST_EXAMPLE["name"]}
CATEGORY_RESPONSE_EXAMPLE = {**REQUEST_EXAMPLE, "id": 2333}

@extend_schema_view(
    orphans_categories=extend_schema(
        description="Получение списка категорий без родительской категории (доступно для всех пользователей)",
        summary="Получение списка без родительской категории",
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                    ),
                ],
            ),
        },
    ),
    popular_categories=extend_schema(
        description="Получение списка популярных категорий (доступно для всех пользователей)",
        summary="Получение списка популярных категорий",
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                    ),
                ],
            ),
        },
    ),
    list=extend_schema(
        description="Получить список всех категорий",
        summary="Список категорий",
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                    ),
                ],
            ),
        },
    ),
    create=extend_schema(
        description="Создать новую категорию",
        summary="Создание категории",
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=REQUEST_EXAMPLE,
                description="Пример запроса на создание новой категории в Swagger UI",
                summary="Пример запроса на создание новой категории",
                media_type="application/json",
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=CategorySerializer(),
                examples=[
                    OpenApiExample(
                        name="Create Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                    ),
                ],
            ),
        },
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретной категории",
        summary="Информация о категории",
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(),
                examples=[
                    OpenApiExample(
                        name="Retrieve Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                    ),
                ],
            ),
        },
    ),
    retrieve_by_slug=extend_schema(
        description="Получить информацию о конкретной категории по слагу",
        summary="Получение категории по слагу",
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(),
                examples=[
                    OpenApiExample(
                        name="Retrieve Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                    ),
                ],
            ),
        },
    ),
    update=extend_schema(
        description="Обновить информацию о категории",
        summary="Обновление категории",
        request=CategorySerializer(),
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=REQUEST_EXAMPLE,
                description="Пример запроса на обновление категории в Swagger UI",
                summary="Пример запроса на обновление категории",
                media_type="application/json",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(),
                examples=[
                    OpenApiExample(
                        name="Update Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                        description="Пример ответа на обновление информации о категории в Swagger UI",
                        summary="Пример ответа на обновление информации о категории",
                        media_type="application/json",
                    ),
                ],
            ),
        },
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о категории",
        summary="Частичное обновление категории",
        request=CategorySerializer(),
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value=PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление категории в Swagger UI",
                summary="Пример запроса на частичное обновление категории",
                media_type="application/json",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(),
                examples=[
                    OpenApiExample(
                        name="Partial Update Response Example",
                        response_only=True,
                        value=CATEGORY_RESPONSE_EXAMPLE,
                        description="Пример ответа на частичное обновление информации о категории в Swagger UI",
                        summary="Пример ответа на частичное обновление информации о категории",
                        media_type="application/json",
                    ),
                ],
            ),
        },
    ),
    destroy=extend_schema(
        description="Удалить категорию",
        summary="Удаление категории",
        responses={204: None},
    ),
)
@extend_schema(tags=["Shop"])
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_serializer_class(self):
        if self.action in ["retrieve", "popular_categories"]:
            return CategoryDetailSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "popular_categories":
            return [AllowAny()]

        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="orphans-categories")
    def orphans_categories(self, request, *args, **kwargs):
        self.queryset = self.filter_queryset(
            self.get_queryset().filter(parent__isnull=True)
        )
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def popular_categories(self, request, *args, **kwargs):
        """
        Кастомное действие для получения популярных категорий.
        """
        self.queryset = self.queryset.filter(is_popular=True)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="by-slug/(?P<slug>[^/.]+)")
    def retrieve_by_slug(self, request, slug=None):
        """
        Кастомное действие для получения категории по слагу.
        """
        category = get_object_or_404(Category, slug=slug)
        serializer = self.get_serializer(category)
        return Response(serializer.data)
