from loguru import logger
from typing import Any, Dict
from celery import shared_task
from django.conf import settings
from crm_integration.factories import CRMFactory
from crm_integration.adapters import OrderCRMAdapter


@shared_task
def create_order_in_crm_task(order_data: Dict[str, Any]):
    """Асинхронная задача для создания заказа в CRM."""

    try:
        api: OrderCRMAdapter = CRMFactory.get_adapter(settings.BASE_CRM)
    except KeyError as err:
        logger.error(f"KeyError while getting crm adapter: {err}")
    api.crm_create_order(order_data)
