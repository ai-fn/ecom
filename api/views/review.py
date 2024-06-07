from rest_framework.viewsets import ModelViewSet
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.review import ReviewSerializer
from shop.models import Review

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["Reviews"])
class ReviewViewSet(ModelViewSet):
    """Возвращает отзывы

    Args:
        viewsets (_type_): _description_
    """

    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех отзывов",
        summary="Список отзывов",
        responses={200: ReviewSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "product": 3732,
                    "name": "John Doe",
                    "raview": "I really enjoyed using this product. Highly recommended!",
                    "rating": 5,
                    "created_at": "2024-03-12T12:00:00Z",
                },
                description="Пример ответа для получения списка всех отзывов в Swagger UI",
                summary="Пример ответа для получения списка всех отзывов",
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Создать новый отзыв",
        summary="Создание отзыва",
        request=ReviewSerializer,
        responses={201: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value={
                    "product": 4537,
                    "name": "John Doe",
                    "rating": 5,
                    "review": "Great product!",
                },
                description="Пример запроса на создание нового отзыва в Swagger UI",
                summary="Пример запроса на создание нового отзыва",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value={
                    "id": 3,
                    "product": 68342,
                    "name": "John Doe",
                    "rating": 5,
                    "review": "Great product!",
                    "created_at": "2024-03-12T15:00:00Z",
                },
                description="Пример ответа на создание нового отзыва в Swagger UI",
                summary="Пример ответа на создание нового отзыва",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о конкретном отзыве",
        summary="Обновление отзыва",
        request=ReviewSerializer,
        responses={200: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value={"rating": 4, "review": "Good product, could be better."},
                description="Пример запроса на обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "product": 32154,
                    "name": "John Doe",
                    "rating": 4,
                    "review": "Good product, could be better.",
                    "created_at": "2024-03-12T12:00:00Z",
                },
                description="Пример ответа на обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример ответа на обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о конкретном отзыве",
        summary="Частичное обновление отзыва",
        request=ReviewSerializer,
        responses={200: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value={"review": "Updated review content."},
                description="Пример запроса на частичное обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "product": 325432,
                    "name": "John Doe",
                    "rating": 4,
                    "review": "Updated review content.",
                    "created_at": "2024-03-12T12:00:00Z",
                },
                description="Пример ответа на частичное обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Удалить отзыв",
        summary="Удаление отзыва",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном отзыве",
        summary="Информация об отзыве",
        responses={200: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "product": 5248,
                    "name": "John Doe",
                    "rating": 5,
                    "review": "Great product!",
                    "created_at": "2024-03-12T12:00:00Z",
                },
                description="Пример ответа для получения информации о конкретном отзыве в Swagger UI",
                summary="Пример ответа для получения информации о конкретном отзыве",
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
