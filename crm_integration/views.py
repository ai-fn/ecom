from loguru import logger
from rest_framework import status
from django.http.response import HttpResponse
from crm_integration.factories import CRMFactory
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


@extend_schema(
    summary="Обработка входящих вебхуков от CRM систем",
    description="Обработка входящих вебхуков от CRM систем",
    tags=["Webhooks", "CRM Integration"],
    responses={
        200: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "Пример ответа",
                    value=None,
                )
            ],
        )
    },
)
def crm_webhook_view(request, crm_name: str) -> HttpResponse:
    try:
        crm = CRMFactory.get_adapter(crm_name)
    except KeyError as err:
        logger.error(f"KeyError while handle incoming crm webhook: {str(err)}")
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    crm.handle_incoming_webhook(request)
    return HttpResponse(status=status.HTTP_200_OK)
