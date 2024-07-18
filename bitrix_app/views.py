import os
from bitrix_app.bitrix_service import Bitrix24API
from bitrix_app.models import Lead
from bitrix_app.filters import LeadFilterSet
from bitrix_app.serializers import LeadSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from drf_spectacular.utils import extend_schema, OpenApiExample, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action


@extend_schema(
    tags=["bitrix"],   
)
@extend_schema_view(
    list=extend_schema(
        summary="Список всех лидов",
        description="Получение списка всех лидов",
        responses={200: LeadSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Пример ответа',
                value=[
                    {
                        'id': 1,
                        'bitrix_id': 123,
                        'title': 'Название лида',
                        'status': 'NEW',
                    },
                    {
                        'id': 2,
                        'bitrix_id': 124,
                        'title': 'Еще одно название лида',
                        'status': 'IN_PROGRESS',
                    }
                ],
                response_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Получить лид",
        description="Получение конкретного лида по ID",
        responses={200: LeadSerializer},
        examples=[
            OpenApiExample(
                'Пример ответа',
                value={
                    'id': 1,
                    'bitrix_id': 123,
                    'title': 'Название лида',
                    'status': 'NEW',
                },
                response_only=True
            )
        ]
    ),
    create=extend_schema(
        summary="Создать нового лида",
        description="Создание нового лида с предоставленной информацией",
        request=LeadSerializer,
        responses={201: LeadSerializer},
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    'bitrix_id': 125,
                    'title': 'Новое название лида',
                    'status': 'NEW',
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример ответа',
                value={
                    'id': 3,
                    'bitrix_id': 125,
                    'title': 'Новое название лида',
                    'status': 'NEW',
                },
                response_only=True
            )
        ]
    ),
    update=extend_schema(
        summary="Обновить существующего лида",
        description="Обновление лида с предоставленной информацией",
        request=LeadSerializer,
        responses={200: LeadSerializer},
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    'title': 'Обновленное название лида',
                    'status': 'IN_PROGRESS',
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример ответа',
                value={
                    'id': 1,
                    'bitrix_id': 123,
                    'title': 'Обновленное название лида',
                    'status': 'IN_PROGRESS',
                },
                response_only=True
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Частично обновить существующего лида",
        description="Частичное обновление лида с предоставленной информацией",
        request=LeadSerializer,
        responses={200: LeadSerializer},
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    'status': 'CLOSED',
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример ответа',
                value={
                    'id': 1,
                    'bitrix_id': 123,
                    'title': 'Название лида',
                    'status': 'CLOSED',
                },
                response_only=True
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удалить лида",
        description="Удаление лида по его ID",
        responses={204: None}
    )
)
class LeadViewSet(ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeadFilterSet

    @action(methods=['get'], detail=False, url_path='sync-leads')
    def sync_leads(self, request, *args, **kwargs):
        webhook_url = os.getenv("LEAD_WEBHOOK_URL")
        bitrix = Bitrix24API(webhook_url)
        leads_data = bitrix.get_leads()
        
        for lead in leads_data['result']:
            Lead.objects.update_or_create(
                bitrix_id=lead['ID'],
                defaults={
                    'title': lead['TITLE'],
                    'status': lead['STATUS_ID'],
                }
            )
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
