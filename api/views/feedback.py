from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiParameter

from rest_framework.viewsets import ModelViewSet

from blog.models import Feedback
from api.serializers import FeedbackSerializer
from api.permissions import AllowCreateOrAdmin



@extend_schema(
    tags=['blog']
)
@extend_schema_view(
    list=extend_schema(
        summary='Список всех отзывов',
        description='Получение списка всех отзывов.',
        responses={200: FeedbackSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary='Получение отзыва по ID',
        description='Получение отзыва по ID.',
        parameters=[
            OpenApiParameter(name='id', description='ID отзыва', required=True, type=int)
        ],
        responses={200: FeedbackSerializer}
    ),
    create=extend_schema(
        summary='Создание нового отзыва',
        description='Создание нового отзыва.',
        request=FeedbackSerializer,
        responses={201: FeedbackSerializer}
    ),
    update=extend_schema(
        summary='Обновление отзыва по ID',
        description='Обновление отзыва по ID.',
        parameters=[
            OpenApiParameter(name='id', description='ID отзыва', required=True, type=int)
        ],
        request=FeedbackSerializer,
        responses={200: FeedbackSerializer}
    ),
    partial_update=extend_schema(
        summary='Частичное обновление отзыва по ID',
        description='Частичное обновление отзыва по ID.',
        parameters=[
            OpenApiParameter(name='id', description='ID отзыва', required=True, type=int)
        ],
        request=FeedbackSerializer,
        responses={200: FeedbackSerializer}
    ),
    destroy=extend_schema(
        summary='Удаление отзыва по ID',
        description='Удаление отзыва по ID.',
        parameters=[
            OpenApiParameter(name='id', description='ID отзыва', required=True, type=int)
        ],
        responses={204: OpenApiResponse(description='Отзыв успешно удален')}
    )
)
class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowCreateOrAdmin]
