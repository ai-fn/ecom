import unittest

from unittest.mock import patch

from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from bitrix_app.models import Lead
from bitrix_app.tasks import task_sync_leads
from bitrix_app.services.bitrix_service import Bitrix24API

from account.models import CustomUser as User


class LeadViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self._create_user()
        self.client.force_authenticate(user=self.user)
        self.lead = Lead.objects.create(
            bitrix_id=1,
            title="Test Lead",
            status="New",
            dynamical_fields={"TITLE": "Test Lead"},
        )

    def _create_user(self):
        return User.objects.create_user(
            username="testuser", password="testpass", is_staff=True
        )

    @patch.object(Bitrix24API, "get_leads_by_period")
    @patch.object(task_sync_leads, "delay")
    def test_sync_leads(self, mock_task_sync_leads, mock_get_leads_by_period):
        url = reverse("api:bitrix:lead-sync-leads")
        response = self.client.get(url, {"days": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_sync_leads.assert_called_once_with(
            weeks=0, days=10, hours=0, minutes=0
        )
        self.assertIn("Lead synchronization initiated", response.data["detail"])

    @patch.object(Bitrix24API, "add_lead")
    @patch.object(task_sync_leads, "delay")
    def test_create_lead(self, mock_task_sync_leads, mock_add_lead):
        mock_add_lead.return_value = ({"result": 1}, 200)
        url = reverse("api:bitrix:lead-list")
        data = {
            "title": "New Lead",
            "status": "NEW",
            "dynamical_fields": {"TITLE": "New Lead"},
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_add_lead.assert_called_once_with({"fields": data["dynamical_fields"]})
        mock_task_sync_leads.assert_called_once_with(minutes=5)
        self.assertIn("success", response.data["detail"])

    @patch.object(Bitrix24API, "delete_lead")
    def test_destroy_lead(self, mock_delete_lead):
        mock_delete_lead.return_value = ({"result": True}, 200)
        url = reverse("api:bitrix:lead-detail", args=[self.lead.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_lead.assert_called_once_with(str(self.lead.id))

    @patch.object(Bitrix24API, "update_lead")
    def test_update_lead(self, mock_update_lead):
        mock_update_lead.return_value = ({"result": True}, 200)
        url = reverse("api:bitrix:lead-detail", args=[self.lead.id])
        data = {
            "title": "Updated Lead",
            "status": "Updated Status",
            "dynamical_fields": {"TITLE": "new value"},
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_lead.assert_called_once_with(
            self.lead.bitrix_id, {"TITLE": data["title"], "STATUS_ID": data["status"]}
        )

    @patch.object(Bitrix24API, "update_lead")
    def test_partial_update_lead(self, mock_update_lead):
        mock_update_lead.return_value = ({"result": True}, 200)
        url = reverse("api:bitrix:lead-detail", args=[self.lead.id])
        data = {"title": "Partially Updated Lead"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_lead.assert_called_once_with(
            self.lead.bitrix_id, {"TITLE": data["title"]}
        )


if __name__ == "__main__":
    unittest.main()
