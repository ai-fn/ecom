from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.serializers import SearchHistorySerializer
from api.permissions import IsOwner
from shop.models import SearchHistory

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample


@extend_schema_view(
    list=extend_schema(
        summary="Список поисковых запросов",
        description="Возвращает список всех сохраненных поисковых запросов.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример списка поисковых запросов",
                description="Пример ответа, содержащего список поисковых запросов.",
                value={"title": "Пример запроса 1"},
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        summary="Добавить поисковый запрос",
        description="Добавляет новый поисковый запрос.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на добавление поискового запроса",
                description="Пример тела запроса для добавления нового поискового запроса.",
                value={"title": "Новый запрос", "user_id": 1},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при добавлении поискового запроса",
                description="Пример успешного ответа, содержащего добавленный поисковый запрос.",
                value={"title": "Новый запрос"},
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Получить поисковый запрос",
        description="Возвращает сохраненный поисковый запрос по ID.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример ответа для одного поискового запроса",
                description="Пример ответа, содержащего данные одного поискового запроса.",
                value={"title": "Пример запроса"},
                response_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Обновить поисковый запрос",
        description="Обновляет информацию о сохраненном поисковом запросе.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на обновление поискового запроса",
                description="Пример тела запроса для обновления существующего поискового запроса.",
                value={"title": "Обновленный запрос", "user_id": 1},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при обновлении поискового запроса",
                description="Пример успешного ответа, содержащего обновленный поисковый запрос.",
                value={"title": "Обновленный запрос"},
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частично обновить поисковый запрос",
        description="Частично обновляет информацию о сохраненном поисковом запросе.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на частичное обновление поискового запроса",
                description="Пример тела запроса для частичного обновления существующего поискового запроса.",
                value={"title": "Частично обновленный запрос", "user_id": 1},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при частичном обновлении поискового запроса",
                description="Пример успешного ответа, содержащего частично обновленный поисковый запрос.",
                value={"title": "Частично обновленный запрос"},
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удалить поисковый запрос",
        description="Удаляет сохраненный поисковый запрос.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при удалении поискового запроса",
                description="Пример успешного ответа после удаления поискового запроса.",
                value={"detail": "Поисковый запрос успешно удален."},
                response_only=True,
            )
        ],
    ),
)
@extend_schema(tags=["Shop"])
class SearchHistoryViewSet(ModelViewSet):

    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
