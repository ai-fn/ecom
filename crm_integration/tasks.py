from celery import shared_task
from django.conf import settings
from crm_integration.factories import CRMFactory
from crm_integration.adapters import OrderCRMAdapter


@shared_task
def create_order_in_crm_task(order_data: dict):
    """Асинхронная задача для создания заказа в CRM."""

    api: OrderCRMAdapter = CRMFactory.get_adapter(settings.BASE_CRM)
    api.crm_create_order(order_data)
