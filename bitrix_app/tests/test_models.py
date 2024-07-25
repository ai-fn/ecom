from django.test import TestCase
from bitrix_app.models import Lead


class LeadModelTest(TestCase):
    def setUp(self):
        self.lead = Lead.objects.create(
            bitrix_id=12345,
            title="Test Lead",
            status="New",
            dynamical_fields={"source": "web"},
        )

    def test_lead_creation(self):
        self.assertTrue(isinstance(self.lead, Lead))
        self.assertEqual(str(self.lead), "Lead 'Test Lead': New")

    def test_lead_fields(self):
        lead = Lead.objects.get(id=self.lead.id)
        self.assertEqual(lead.bitrix_id, 12345)
        self.assertEqual(lead.title, "Test Lead")
        self.assertEqual(lead.status, "New")
        self.assertEqual(lead.dynamical_fields, {"source": "web"})
        self.assertTrue(lead.is_active)

    def test_auto_fields(self):
        lead = Lead.objects.get(id=self.lead.id)
        self.assertIsNotNone(lead.created_at)
        self.assertIsNotNone(lead.updated_at)
