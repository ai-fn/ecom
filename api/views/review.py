from django_filters import rest_framework as filters

from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from api.filters.review import ReviewFilters
from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.permissions import ReadCreateOrAdminPermission
from api.serializers.review import ReviewSerializer

from shop.models import Review

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample


REVIEW_REQUEST_EXAMPLE = {
    "product": 3732,
    "name": "John Doe",
    "raview": "I really enjoyed using this product. Highly recommended!",
    "rating": 5,
    "created_at": "2024-03-12T12:00:00Z",
    "is_active": True,
}
REVIEW_RESPONSE_EXAMPLE = {"id": 1, **REVIEW_REQUEST_EXAMPLE}
REVIEW_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(REVIEW_REQUEST_EXAMPLE.items())[:2]
}

class CustomProductReviewPagination(PageNumberPagination):
    page_size = 8

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех отзывов",
        summary="Список отзывов",
        responses={200: ReviewSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=REVIEW_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка всех отзывов в Swagger UI",
                summary="Пример ответа для получения списка всех отзывов",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном отзыве",
        summary="Информация об отзыве",
        responses={200: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=REVIEW_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретном отзыве в Swagger UI",
                summary="Пример ответа для получения информации о конкретном отзыве",
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Создать новый отзыв",
        summary="Создание отзыва",
        request=ReviewSerializer,
        responses={201: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=REVIEW_REQUEST_EXAMPLE,
                description="Пример запроса на создание нового отзыва в Swagger UI",
                summary="Пример запроса на создание нового отзыва",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=REVIEW_RESPONSE_EXAMPLE,
                description="Пример ответа на создание нового отзыва в Swagger UI",
                summary="Пример ответа на создание нового отзыва",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о конкретном отзыве",
        summary="Обновление отзыва",
        request=ReviewSerializer,
        responses={200: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=REVIEW_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=REVIEW_RESPONSE_EXAMPLE,
                description="Пример ответа на обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример ответа на обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о конкретном отзыве",
        summary="Частичное обновление отзыва",
        request=ReviewSerializer,
        responses={200: ReviewSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value=REVIEW_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=REVIEW_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о конкретном отзыве в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном отзыве",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить отзыв",
        summary="Удаление отзыва",
        responses={204: None},
    ),
)
@extend_schema(tags=["Reviews"])
class ReviewViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    """Возвращает отзывы

    Args:
        viewsets (_type_): _description_
    """

    queryset = Review.objects.order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [ReadCreateOrAdminPermission]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ReviewFilters


    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        print(request.query_params.get("product"))
        if request.query_params.get("product") is not None:
            self.pagination_class = CustomProductReviewPagination
