from rest_framework.test import APITestCase
from bitrix_app.models import Lead
from bitrix_app.serializers import LeadSerializer


class LeadSerializerTest(APITestCase):
    def setUp(self):
        self.lead_attributes = {
            "bitrix_id": 12345,
            "title": "Test Lead",
            "status": "New",
            "dynamical_fields": {"source": "web"},
            "is_active": True,
        }

        self.lead = Lead.objects.create(**self.lead_attributes)
        self.serializer = LeadSerializer(instance=self.lead)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            set(
                ["id", "bitrix_id", "status", "title", "is_active", "dynamical_fields"]
            ),
        )

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["bitrix_id"], self.lead_attributes["bitrix_id"])
        self.assertEqual(data["title"], self.lead_attributes["title"])
        self.assertEqual(data["status"], self.lead_attributes["status"])
        self.assertEqual(
            data["dynamical_fields"], self.lead_attributes["dynamical_fields"]
        )
        self.assertEqual(data["is_active"], self.lead_attributes["is_active"])

    def test_validate_dynamical_fields(self):
        invalid_data = self.lead_attributes.copy()
        invalid_data["dynamical_fields"] = {"invalid_field": "value"}
        serializer = LeadSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("dynamical_fields", serializer.errors)
        self.assertEqual(
            str(serializer.errors["dynamical_fields"][0]),
            "'invalid_field' is not allow field for lead.",
        )
