import requests

class Bitrix24API:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def get_leads(self):
        url = f"{self.webhook_url}/crm.lead.list"
        response = requests.get(url)
        return response.json()

    def add_lead(self, lead_data):
        url = f"{self.webhook_url}/crm.lead.add"
        response = requests.post(url, json=lead_data)
        return response.json()
