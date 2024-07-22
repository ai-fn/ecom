import requests

from loguru import logger

from datetime import timedelta

from django.utils import timezone
from django.conf import settings


class Bitrix24API:

    _instance = None
    _allowed_fields = None

    def __new__(cls, *args, **kwargs) -> "Bitrix24API":
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self.lead_list_webhook_url = getattr(settings, "LEAD_LIST_WEBHOOK_URL", None)
        self.lead_get_webhook_url = getattr(settings, "LEAD_GET_WEBHOOK_URL", None)
        self.lead_add_webhook_url = getattr(settings, "LEAD_ADD_WEBHOOK_URL", None)
        self.lead_update_webhook_url = getattr(
            settings, "LEAD_UPDATE_WEBHOOK_URL", None
        )
        self.lead_fields_webhook_url = getattr(
            settings, "LEAD_FIELDS_WEBHOOK_URL", None
        )
        self.lead_delete_webhook_url = getattr(
            settings, "LEAD_DELETE_WEBHOOK_URL", None
        )

    def get_allowed_fields(self):
        if self._allowed_fields is None:
            self._allowed_fields = self.get_fields()

        return self._allowed_fields

    def get_response(self, url: str, params: dict = None) -> tuple[dict, int]:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json(), response.status_code
        except requests.RequestException as e:
            logger.error(f"Request failed for GET {url} with params {params}: {e}")
            return {}, response.status_code

    def post_response(self, url: str, data: dict = None) -> tuple[dict, int]:
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json(), response.status_code
        except requests.RequestException as e:
            logger.error(f"Request failed for POST {url} with data {data}: {e}")
            return {}, response.status_code

    def retrieve(self, id: int):
        url = f"{self.lead_get_webhook_url}/crm.lead.get.json"
        return self.get_response(url, params={"id": id})

    def get_leads(self, params: dict = None):
        url = f"{self.lead_list_webhook_url}/crm.lead.list.json"
        return self.get_response(url, params)

    def get_fields(self) -> dict:
        url = f"{self.lead_fields_webhook_url}/crm.lead.fields.json"
        response = requests.get(url)
        fields_data = response.json()

        if "result" in fields_data:
            return fields_data["result"]

        logger.info(
            f"'result' not found in crm.lead.fileds.json response: {response.text}({response.status_code})"
        )
        return {}

    def add_lead(self, lead_data: dict):
        url = f"{self.lead_add_webhook_url}/crm.lead.add.json"
        return self.post_response(url, lead_data)

    def update_lead(self, id: int, fields: dict):
        url = f"{self.lead_update_webhook_url}/crm.lead.update.json"
        json = {
            "id": id,
            "fields": fields,
        }
        return self.post_response(url, data=json)

    def delete_lead(self, id: int):
        url = f"{self.lead_delete_webhook_url}/crm.lead.delete.json"
        return self.post_response(url, data={"id": id})

    def get_leads_by_period(
        self, weeks: int = 0, days: int = 0, hours: int = 0, minutes: int = 0
    ) -> list:
        if not any([weeks, days, hours, minutes]):
            weeks = 4

        leads = []
        start = 0
        batch_size = 50
        date_from = (
            timezone.localtime(timezone.now())
            - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
        ).strftime("%Y-%m-%dT%H:%M:%S")
        params = {"filter[>=DATE_CREATE]": date_from}

        while True:
            params["start"] = start
            leads_data, _ = self.get_leads(params)

            if "error" in leads_data:
                logger.error(
                    f"Error from Bitrix24 while getting leads with params {params}: {leads_data}"
                )

            current_batch = leads_data.get("result", [])
            leads.extend(current_batch)

            if len(current_batch) < batch_size:
                break

            start += batch_size

        return leads