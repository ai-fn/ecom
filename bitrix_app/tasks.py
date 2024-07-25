from datetime import timedelta
from celery import shared_task
from loguru import logger

from django.utils import timezone
from django.db import transaction

from bitrix_app.models import Lead
from bitrix_app.services.bitrix_service import Bitrix24API


@shared_task
def task_sync_leads(weeks: int = 0, days: int = 0, hourse: int = 0, minutes: int = 0):
    bitrix = Bitrix24API()
    leads = bitrix.get_leads_by_period(weeks=weeks, days=days, hours=hourse, minutes=minutes)

    try:
        with transaction.atomic():
            for lead in leads:
                Lead.objects.update_or_create(
                    bitrix_id=lead['ID'],
                    defaults={
                        'title': lead['TITLE'],
                        'status': lead['STATUS_ID'],
                        'dynamical_fields': lead
                    }
                )
    except Exception as e:
        logger.error(f"Error while synchronizing leads: {e}")
        raise

    from_date = (timezone.localtime(timezone.now()) - timedelta(weeks=weeks, days=days, hours=hourse, minutes=minutes)).strftime("%d-%m-%Y %H:%M")
    logger.info(f"Leads successfully synchronized for the period from {from_date} to now.")
