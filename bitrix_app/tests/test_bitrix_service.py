import unittest
from unittest.mock import patch, MagicMock
from django.conf import settings
from bitrix_app.services.bitrix_service import Bitrix24API


class TestBitrix24API(unittest.TestCase):
    
    @patch('requests.get')
    def test_get_allowed_fields(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "TITLE": {"type": "string", "isRequired": False},
                "STATUS_ID": {"type": "string", "isRequired": False}
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        api = Bitrix24API()
        fields = api.get_allowed_fields()
        self.assertIn("TITLE", fields)
        self.assertIn("STATUS_ID", fields)
        self.assertEqual(fields["TITLE"]["type"], "string")
        self.assertEqual(fields["STATUS_ID"]["type"], "crm_status")

    @patch('requests.get')
    def test_retrieve(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": {"ID": "1", "TITLE": "Test Lead"}}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        api = Bitrix24API()
        lead, status_code = api.retrieve(1)
        self.assertEqual(status_code, 200)
        self.assertEqual(lead["result"]["TITLE"], "Test Lead")

    @patch('requests.post')
    def test_add_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 1}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = Bitrix24API()
        lead_data = {"TITLE": "New Lead"}
        result, status_code = api.add_lead(lead_data)
        self.assertEqual(status_code, 200)
        self.assertEqual(result["result"], 1)

    @patch('requests.post')
    def test_update_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = Bitrix24API()
        lead_data = {"TITLE": "Updated Lead"}
        result, status_code = api.update_lead(1, lead_data)
        self.assertEqual(status_code, 200)
        self.assertTrue(result["result"])

    @patch('requests.post')
    def test_delete_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = Bitrix24API()
        result, status_code = api.delete_lead(1)
        self.assertEqual(status_code, 200)
        self.assertTrue(result["result"])

    @patch('requests.get')
    def test_get_leads_by_period(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": [{"ID": "1", "TITLE": "Test Lead"}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        api = Bitrix24API()
        leads = api.get_leads_by_period(weeks=1)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["TITLE"], "Test Lead")

if __name__ == "__main__":
    unittest.main()
