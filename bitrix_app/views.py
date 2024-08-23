from loguru import logger

from api.mixins import IntegrityErrorHandlingMixin, ActiveQuerysetMixin

from bitrix_app.services.bitrix_service import Bitrix24API
from bitrix_app.models import Lead
from bitrix_app.filters import LeadFilterSet
from bitrix_app.tasks import task_sync_leads
from bitrix_app.serializers import LeadSerializer

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    extend_schema_view,
    OpenApiParameter,
)
from django_filters.rest_framework import DjangoFilterBackend


create_lead_example = {
    "title": "Еще одно название лида",
    "status": "+79********* - Входящий звонок",
    "status": "IN_PROGRESS",
    "dynamical_fields": {
        "ID": "31805",
        "NAME": None,
        "POST": None,
        "TITLE": "+79********* - Входящий звонок",
        "OPENED": "Y",
        "ADDRESS": None,
        "COMMENTS": None,
        "HAS_IMOL": "N",
        "UTM_TERM": None,
        "ADDRESS_2": None,
        "BIRTHDATE": "",
        "HAS_EMAIL": "N",
        "HAS_PHONE": "Y",
        "HONORIFIC": None,
        "LAST_NAME": None,
        "ORIGIN_ID": None,
        "SOURCE_ID": "3",
        "STATUS_ID": "1",
        "COMPANY_ID": None,
        "CONTACT_ID": None,
        "MOVED_TIME": "2021-04-03T15:20:48+03:00",
        "UTM_MEDIUM": None,
        "UTM_SOURCE": None,
        "CURRENCY_ID": "RUB",
        "DATE_CLOSED": "2021-04-03T15:20:47+03:00",
        "DATE_CREATE": "2021-04-02T18:00:01+03:00",
        "DATE_MODIFY": "2021-04-03T15:20:47+03:00",
        "MOVED_BY_ID": "39",
        "OPPORTUNITY": "0.00",
        "SECOND_NAME": None,
        "UTM_CONTENT": None,
        "ADDRESS_CITY": None,
        "MODIFY_BY_ID": "39",
        "UTM_CAMPAIGN": None,
        "COMPANY_TITLE": None,
        "CREATED_BY_ID": "13",
        "ORIGINATOR_ID": None,
        "ADDRESS_REGION": None,
        "ASSIGNED_BY_ID": "39",
        "ADDRESS_COUNTRY": None,
        "ADDRESS_PROVINCE": None,
        "LAST_ACTIVITY_BY": "13",
        "IS_RETURN_CUSTOMER": "N",
        "LAST_ACTIVITY_TIME": "2021-04-02T18:00:01+03:00",
        "SOURCE_DESCRIPTION": "Звонок поступил на номер: +79*********.",
        "STATUS_DESCRIPTION": None,
        "STATUS_SEMANTIC_ID": "F",
        "ADDRESS_LOC_ADDR_ID": None,
        "ADDRESS_POSTAL_CODE": None,
        "ADDRESS_COUNTRY_CODE": None,
        "IS_MANUAL_OPPORTUNITY": "N",
    },
}
lead_example = {
    "id": 2,
    "bitrix_id": 124,
    **create_lead_example,
}
by_bitrix_id_param = OpenApiParameter(
    name="by_bitrix_id",
    type=bool,
    default=False,
    required=False,
)


@extend_schema(tags=["bitrix"])
@extend_schema_view(
    list=extend_schema(
        summary="Список всех лидов",
        description="Получение списка всех лидов",
        responses={200: LeadSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Пример ответа",
                value=lead_example,
                response_only=True,
            )
        ],
    ),
    sync_leads=extend_schema(
        summary="Синхронихировать лиды",
        description="Синхронихировать лиды",
        parameters=[
            OpenApiParameter(
                name="weeks",
                type=int,
                description="Период для синхронизации (в неделях)",
                default=4,
                required=False,
            ),
            OpenApiParameter(
                name="days",
                type=int,
                description="Период для синхронизации (в днях)",
                default=0,
                required=False,
            ),
            OpenApiParameter(
                name="hours",
                type=int,
                description="Период для синхронизации (в часах)",
                default=0,
                required=False,
            ),
            OpenApiParameter(
                name="minutes",
                type=int,
                description="Период для синхронизации (в минутах)",
                default=0,
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Получить лид",
        description="Получение конкретного лида по ID",
        responses={200: LeadSerializer},
        parameters=[by_bitrix_id_param],
        examples=[
            OpenApiExample(
                "Пример ответа",
                value=lead_example,
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        summary="Создать нового лида",
        description="Создание нового лида с предоставленной информацией",
        request=LeadSerializer,
        responses={201: LeadSerializer},
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=create_lead_example,
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value=lead_example,
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Обновить существующего лида",
        description="Обновление лида с предоставленной информацией",
        request=LeadSerializer,
        responses={200: LeadSerializer},
        parameters=[by_bitrix_id_param],
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "title": "Обновленное название лида",
                    "status": "IN_PROGRESS",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value=lead_example,
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частично обновить существующего лида",
        description="Частичное обновление лида с предоставленной информацией",
        request=LeadSerializer,
        parameters=[by_bitrix_id_param],
        responses={200: LeadSerializer},
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "status": "CLOSED",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value=lead_example,
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удалить лида по его ID",
        description="Удаление лида по его ID",
        parameters=[by_bitrix_id_param],
        responses={204: None},
    ),
)
class LeadViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeadFilterSet
    bitrix = Bitrix24API()

    def get_object(self):
        if self.request.query_params.get("by_bitrix_id") == "true":
            lookup_field = self.lookup_url_kwarg or self.lookup_field
            prev_value = self.kwargs[lookup_field]
            self.lookup_url_kwarg = self.lookup_field = "bitrix_id"
            self.kwargs[self.lookup_field] = prev_value

        return super().get_object()

    @action(methods=["get"], detail=False, url_path="sync-leads")
    def sync_leads(self, request, *args, **kwargs):
        weeks = int(request.query_params.get("weeks", 0))
        days = int(request.query_params.get("days", 0))
        hours = int(request.query_params.get("hours", 0))
        minutes = int(request.query_params.get("minutes", 0))
        if not any([weeks, days, hours, minutes]):
            weeks = 4

        task_sync_leads.delay(weeks=weeks, days=days, hours=hours, minutes=minutes)
        logger.info(
            f"Lead sync task started by user '{request.user.username}' from ip '{request.META.get('REMOTE_ADDR')}'"
        )
        return Response(
            {"detail": "Lead synchronization initiated"}, status=HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        response = super().create(
            request, *args, **kwargs
        )
        if 200 <= response.status_code < 400:

            lead_data = {"fields": request.data.get("dynamical_fields")}
            response, status = self.bitrix.add_lead(lead_data)

            if not 200 <= status < 400:
                self.log_error(request, response, status, "creating lead")
                return Response(response, status=status)

            task_sync_leads.delay(minutes=5)
            return Response({"detail": "success"}, status=HTTP_201_CREATED)

        return response

    def destroy(self, request, *args, **kwargs):
        response, status = self.bitrix.delete_lead(kwargs[self.lookup_field])
        if not 200 <= status < 400:
            self.log_error(request, response, status, "deleting lead")
            return Response(response, status=status)

        return super().destroy(request, *args, **kwargs)


    def update(self, request, *args, **kwargs) -> Response:
        response = super().update(
            request, *args, **kwargs
        )
        if 200 <= response.status_code < 400:
            update_data = self.get_update_data(request.data)
            
            response_data, status = self.bitrix.update_lead(
                response.data["bitrix_id"], update_data
            )
            if not 200 <= status < 400:
                self.log_error(request, response_data, status, "updating lead")
            return Response(response_data, status=status)

        return response

    def partial_update(self, request, *args, **kwargs) -> Response:
        return super().partial_update(request, *args, **kwargs)

    def get_update_data(self, data: dict) -> dict:
        update_data = data.get("dynamical_fields", {})
        if title := data.get("title"):
            update_data["TITLE"] = title
        if status := data.get("status"):
            update_data["STATUS_ID"] = status

        return update_data

    def log_error(self, request, response: dict, status: int, action: str):
        logger.info(
            f"Error {action} by user '{request.user.username}' with IP '{request.META.get('REMOTE_ADDR')}'"
        )
        logger.error(f"Error while {action}: '{response}' (status {status})")
