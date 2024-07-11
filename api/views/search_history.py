from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.decorators import action

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
                value={
                    "id": 1,
                    "title": "Новый запрос",
                    "is_active": True,
                },
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
                summary="Пример запроса на добавление поискового запроса (с указанием user_id)",
                description="Пример тела запроса для добавления нового поискового запроса.",
                value={
                    "title": "Новый запрос",
                    "user_id": 1,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на добавление поискового запроса (без указания user_id)",
                description="Пример тела запроса для добавления нового поискового запроса.",
                value={
                    "title": "Новый запрос",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при добавлении поискового запроса",
                description="Пример успешного ответа, содержащего добавленный поисковый запрос.",
                value={
                    "id": 1,
                    "title": "Новый запрос",
                    "is_active": True,
                },
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
                value={
                    "id": 1,
                    "title": "Пример запроса",
                    "is_active": True,
                },
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
                value={
                    "title": "Обновленный запрос",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при обновлении поискового запроса",
                description="Пример успешного ответа, содержащего обновленный поисковый запрос.",
                value={
                    "id": 1,
                    "title": "Обновленный запрос",
                    "is_active": True,
                },
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
                value={
                    "title": "Частично обновленный запрос",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при частичном обновлении поискового запроса",
                description="Пример успешного ответа, содержащего частично обновленный поисковый запрос.",
                value={
                    "id": 1,
                    "title": "Частично обновленный запрос",
                    "is_active": True,
                },
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
                response_only=True,
            )
        ],
    ),
)
@extend_schema(tags=["Shop"])
class SearchHistoryViewSet(ModelViewSet):

    queryset = SearchHistory.objects.all().order_by("-created_at")
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        if self.action == "list":
            return queryset[:10]

        return queryset

    def create(self, request, *args, **kwargs):
        if not request.data.get("user_id"):
            request.data["user_id"] = self.request.user.pk

        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Очистка истории поиска",
        summary="Очистка истории поиска",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Request Example",
                value={},
            ),
        ],
    )
    @action(detail=False, methods=["delete"])
    def clear_history(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response([], status=HTTP_204_NO_CONTENT)
