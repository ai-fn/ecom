import unittest

from unittest.mock import patch
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from bitrix_app.tasks import task_sync_leads
from bitrix_app.tasks import task_sync_leads


class TaskSyncLeadsTest(TestCase):

    @patch('bitrix_app.services.bitrix_service.Bitrix24API.get_leads_by_period')
    @patch('bitrix_app.models.Lead.objects.update_or_create')
    def test_task_sync_leads(self, mock_update_or_create, mock_get_leads_by_period):
        mock_get_leads_by_period.return_value = [
            {
                'ID': '1',
                'TITLE': 'Test Lead 1',
                'STATUS_ID': 'New',
                'CUSTOM_FIELD': 'Value'
            },
            {
                'ID': '2',
                'TITLE': 'Test Lead 2',
                'STATUS_ID': 'In Progress',
                'CUSTOM_FIELD': 'Another Value'
            }
        ]
        
        task_sync_leads(weeks=1)
        
        self.assertEqual(mock_update_or_create.call_count, 2)
        
        mock_update_or_create.assert_any_call(
            bitrix_id='1',
            defaults={
                'title': 'Test Lead 1',
                'status': 'New',
                'dynamical_fields': {
                    'ID': '1',
                    'TITLE': 'Test Lead 1',
                    'STATUS_ID': 'New',
                    'CUSTOM_FIELD': 'Value'
                }
            }
        )
        
        mock_update_or_create.assert_any_call(
            bitrix_id='2',
            defaults={
                'title': 'Test Lead 2',
                'status': 'In Progress',
                'dynamical_fields': {
                    'ID': '2',
                    'TITLE': 'Test Lead 2',
                    'STATUS_ID': 'In Progress',
                    'CUSTOM_FIELD': 'Another Value'
                }
            }
        )

    @patch('bitrix_app.services.bitrix_service.Bitrix24API.get_leads_by_period')
    @patch('bitrix_app.models.Lead.objects.update_or_create')
    @patch('bitrix_app.tasks.logger')
    def test_task_sync_leads_logging(self, mock_logger, mock_update_or_create, mock_get_leads_by_period):
        mock_get_leads_by_period.return_value = []
        
        task_sync_leads(weeks=1)
        
        mock_logger.info.assert_called_once()
        from_date = (timezone.localtime(timezone.now()) - timedelta(weeks=1)).strftime("%d-%m-%Y %H:%M")
        mock_logger.info.assert_called_with(f"Leads successfully synchronized for the period from {from_date} to now.")

if __name__ == "__main__":
    unittest.main()
