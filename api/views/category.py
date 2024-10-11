from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from api.mixins import (
    ActiveQuerysetMixin,
    IntegrityErrorHandlingMixin,
    CacheResponse,
)
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import (
    CategorySerializer,
    CategorySimplifiedSerializer,
    CategoryDetailSerializer,
    CategoryOrphanSerializer,
)
from django.shortcuts import get_object_or_404
from shop.models import Category
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
)


REQUEST_EXAMPLE = {
    "name": "Гидро-ветрозащита и пароизоляция",
    "h1_tag": "dummy_h1_tag",
    "slug": "gidro-vetrozashchita-i-paroizoliatsiia",
    "order": 2333,
    "parent": 2348,
    "description": "dummy_description",
    "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "image": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "thumb_img": "base64string",
    "is_acitve": True,
    "is_popular": True,
    "is_visible": True,
}
CATEGORY_DETAIL_RESPONSE_EXAMPLE = {
    "id": 1088,
    **REQUEST_EXAMPLE,
}

PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(REQUEST_EXAMPLE.items())[:2]}
CATEGORY_RESPONSE_EXAMPLE = {
    "id": 2333,
    **REQUEST_EXAMPLE,
    "children": [
        {
            "id": 2348,
            "name": "Армирующая ткань АЛЬФА ПЭЙСТ",
            "h1_tag": "dummy_h1_tag",
            "slug": "armiruiushchaia-tkan-al-fa-peist",
            "order": 2348,
            "parent": 2333,
            "description": "dummy_description",
            "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
            "image": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
            "thumb_img": "base64string",
            "is_visible": True,
            "is_popular": False,
            "is_acitve": True,
            "children": [],
            "parents": [],
        },
    ],
    "parents": [
        ["Кровельные материалы", "krovelnye-materialy"],
        ["Вентиляционные системы", "ventiliatsionnye-sistemy"],
        ["Аэраторы", "aeratory"],
    ],
}
CATEGORY_SIMPLIFIED_RESPONSE_EXAMPLE = {
    "id": 650,
    "name": "Кровельные материалы",
    "slug": "krovelnye-materialy",
    "description": "dummy_description",
    "parents": [
        ["Кровельные материалы", "krovelnye-materialy"],
        ["Вентиляционные системы", "ventiliatsionnye-sistemy"],
        ["Аэраторы", "aeratory"],
    ],
    "icon": "/media/catalog/categories/images/some-image.webp",
    "image": "/media/catalog/categories/images/some-image.webp",
    "is_active": True,
}


@extend_schema_view(
    orphans_categories=extend_schema(
        parameters=[OpenApiParameter(
            "city_domain",
            type=str,
            required=False,
        )],
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
                        value=CATEGORY_DETAIL_RESPONSE_EXAMPLE,
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
                        value=CATEGORY_DETAIL_RESPONSE_EXAMPLE,
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
                        value=CATEGORY_SIMPLIFIED_RESPONSE_EXAMPLE,
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
class CategoryViewSet(
    ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet
):
    queryset = Category.objects.order_by("order")
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def initial(self, request, *args, **kwargs):
        self.domain = request.query_params.get("city_domain", "")
        return super().initial(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(is_visible=True)

    def get_serializer_class(self):
        if self.action in ["retrieve", "popular_categories"]:
            return CategoryDetailSerializer

        elif self.action == "orphans_categories":
            return CategoryOrphanSerializer

        elif self.action == "retrieve_by_slug":
            return CategorySimplifiedSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "popular_categories":
            return [AllowAny()]

        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="orphans-categories")
    def orphans_categories(self, request, *args, **kwargs):
        self.queryset = self.filter_queryset(
            self.get_queryset().filter(
                products__isnull=False,
                products__prices__city_group__cities__domain=self.domain,
            )
        ).distinct()
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
