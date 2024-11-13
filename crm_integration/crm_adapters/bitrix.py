import requests

from loguru import logger
from django.conf import settings

from account.models import City
from cart.models import Order, ProductsInOrder
from crm_integration.abs import CRMInterface


class BitrixAPI(CRMInterface):

    get_user_webhook_url = getattr(settings, "GET_USER_WEBHOOK_URL", None)
    lead_add_webhook_url = getattr(settings, "LEAD_ADD_WEBHOOK_URL", None)
    lead_update_webhook_url = getattr(settings, "LEAD_UPDATE_WEBHOOK_URL", None)

    @classmethod
    def handle_order_creation(cls, order, domain):
        cls.create_lead_for_order(order, domain)
        return

    @classmethod
    def handle_incoming_webhook(cls, data: dict):
        return super().handle_incoming_webhook(data)

    @classmethod
    def handle_outgoing_webhook(cls, data: dict):
        return super().handle_outgoing_webhook(data)

    @classmethod
    def _get_user(cls, email: str) -> dict:
        url = f"{cls.get_user_webhook_url}/user.get.json"
        resp = cls.post_response(url, params={"EMAIL": email})
        user_data = resp[0].get(
            "result",
            [
                {},
            ],
        )[0]
        return user_data

    @classmethod
    def get_default_lead_user(cls):
        default_lead_user_email = getattr(settings, "DEFAULT_LEAD_USER_EMAIL", None)
        result = cls._get_user(email=default_lead_user_email)
        return result

    @classmethod
    def create_lead_for_order(cls, order: Order, domain: str):
        lead_user_id = cls.get_default_lead_user().get("ID")
        city = City.objects.filter(domain=domain).first()
        city_name = getattr(city, "name", None)

        ordered_prods = ProductsInOrder.objects.filter(order=order)
        comment = "\n".join(
            [
                f"{op.product.title}\n\tКоличество: {op.quantity}\n\tЦена: {float(op.price)}"
                for op in ordered_prods
            ]
        )

        get_name = lambda fn, ln: f"{fn} {ln}".strip()
        customer_name = (
            get_name(order.customer.first_name, order.customer.last_name)
            if order.customer.first_name and order.customer.last_name
            else get_name(order.receiver_first_name, order.receiver_last_name)
        )
        phone = order.receiver_phone if order.customer.phone is None else order.customer.phone

        lead_data = {
            "fields": {
                "TITLE": f"{phone} Заказ от {customer_name}",
                "ASSIGNED_BY_ID": lead_user_id,
                "OPENED": "N",
                "STATUS_ID": "NEW",
                "ADDRESS": order.address,
                "NAME": customer_name.split()[0],
                "UF_CRM_1725873647873": customer_name.split()[0],
                "LAST_NAME": customer_name.split()[1],
                "CURRENCY_ID": "RUB",
                "OPPORTUNITY": float(order.total),
                "UF_CRM_1726038229797": float(order.total),
                "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
                "WEB": [{"VALUE": domain, "VALUE_TYPE": "WORK"}],
                "UF_CRM_1586436329935": city_name,
                "COMMENTS": comment,
                "UF_CRM_1726050625737": comment,
            },
            "params": {"REGISTER_SONET_EVENT": "Y"},
        }

        result, status = cls._add_lead(lead_data)
        if not 200 <= status < 400:
            logger.error(f"Order Lead creation failed, response data: {result}")
        return result

    @classmethod
    def get_response(cls, url: str, params: dict = None) -> tuple[dict, int]:
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
            return response.json(), response.status_code
        except requests.RequestException as e:
            logger.error(f"Request failed for GET {url} with params {params}: {e}")
            return {}, response.status_code

    @classmethod
    def post_response(
        cls, url: str, data: dict = None, params: dict = None
    ) -> tuple[dict, int]:
        response = requests.post(url, json=data, params=params)
        try:
            response.raise_for_status()
            return response.json(), response.status_code
        except requests.RequestException as e:
            logger.error(f"Request failed for POST {url} with data {data}: {e}")
            return {}, response.status_code

    @classmethod
    def _add_lead(cls, lead_data: dict):
        url = f"{cls.lead_add_webhook_url}/crm.lead.add.json"
        return cls.post_response(url, lead_data)

    @classmethod
    def update_lead(cls, id: int, fields: dict):
        url = f"{cls.lead_update_webhook_url}/crm.lead.update.json"
        json = {
            "id": id,
            "fields": fields,
        }
        return cls.post_response(url, data=json)
