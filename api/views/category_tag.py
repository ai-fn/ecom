from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import action

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)

from api.serializers import CategoryTagSerializer, CategoryTagDetailSerializer
from shop.models import Category, CategoryTag


CATEGORY_TAG_REQUEST = {
    "parent": 1,
    "name": "Dummy Name",
    "category_slug": "dummy-name",
}
CATEGORY_TAG_RESPONSE = {
    "id": 1,
    **CATEGORY_TAG_REQUEST,
}
CATEGORY_TAG_DETAIL_REQUEST = {
    **CATEGORY_TAG_REQUEST,
    "order": 1,
    "created_at": "2024-10-17T13:49:40.818Z",
    "updated_at": "2024-10-17T13:49:40.818Z",
    "is_active": True,
}
CATEGORY_TAG_DETAIL_RESPONSE = {"id": 1, **CATEGORY_TAG_DETAIL_REQUEST}
CATEGORY_TAG_DETAIL_PARTIAL_UPDATE_REQUEST = {k: v for k, v in list(CATEGORY_TAG_DETAIL_REQUEST.items())[:3]}

@extend_schema(tags=["api"])
@extend_schema_view(
    list=extend_schema(
        summary="Получения информации о тегах категорий",
        description="Получения информации о тегах категорий",
        responses={
            200: OpenApiResponse(
                response=CategoryTagDetailSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        response_only=True,
                        value=CATEGORY_TAG_DETAIL_RESPONSE,
                    )
                ],
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получение информации о конкретном тэге",
        description="Получение информации о конкретном тэге",
        responses={
            200: OpenApiResponse(
                response=CategoryTagDetailSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        response_only=True,
                        value=CATEGORY_TAG_DETAIL_RESPONSE,
                    )
                ],
            )
        },
    ),
    create=extend_schema(
        summary="Создание тэга категории",
        description="Создание тэга категории",
        examples=[OpenApiExample(
            "Пример запроса",
            request_only=True,
            value=CATEGORY_TAG_DETAIL_REQUEST,
        )],
        responses={
            200: OpenApiResponse(
                response=CategoryTagDetailSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        response_only=True,
                        value=CATEGORY_TAG_DETAIL_RESPONSE,
                    ),
                ],
            )
        },
    ),
    update=extend_schema(
        summary="Обновление информации тэга категории",
        description="Обновление информации тэга категории",
        examples=[OpenApiExample(
            "Пример запроса",
            request_only=True,
            value=CATEGORY_TAG_DETAIL_REQUEST,
        )],
        responses={
            200: OpenApiResponse(
                response=CategoryTagDetailSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        response_only=True,
                        value=CATEGORY_TAG_DETAIL_RESPONSE,
                    ),
                ],
            )
        },
    ),
    partial_update=extend_schema(
        summary="Частичное обновление тэга категории",
        description="Частичное обновление тэга категории",
        examples=[OpenApiExample(
            "Пример запроса",
            request_only=True,
            value=CATEGORY_TAG_DETAIL_PARTIAL_UPDATE_REQUEST,
        )],
        responses={
            200: OpenApiResponse(
                response=CategoryTagDetailSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        response_only=True,
                        value=CATEGORY_TAG_DETAIL_RESPONSE,
                    ),
                ],
            )
        },
    ),
    destroy=extend_schema(
        summary="Удаление тэга категории",
        description="Удаление тэга категории",
        responses={204: None},
    ),
    get_by_slug=extend_schema(
        summary="Получение информации о тэга для категории по её слагу",
        description="Получение информации о тэга для категории по её слагу",
        responses={
            200: OpenApiResponse(
                response=CategoryTagSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        response_only=True,
                        value=CATEGORY_TAG_RESPONSE,
                    )
                ],
            ),
        },
    ),
)
class CategoryTagViewSet(ModelViewSet):
    queryset = CategoryTag.objects.all()
    serializer_class = CategoryTagDetailSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == "get_by_slug":
            return [AllowAny()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "get_by_slug":
            return CategoryTagSerializer

        return super().get_serializer_class()

    @action(detail=False, methods=["get"], url_path="by-slug/(?P<category_slug>[^/.]+)")
    def get_by_slug(self, request, *args, slug: str = None, **kwargs):
        ctg = Category.objects.filter(slug=slug).first()
        if not ctg:
            self.queryset = self.queryset.none()
        else:
            self.queryset = ctg.category_tags.all()

        return super().list(request, *args, **kwargs)
