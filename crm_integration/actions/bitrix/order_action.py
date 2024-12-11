
import asyncio
from loguru import logger
from account.models import City
from django.conf import settings
from asgiref.sync import sync_to_async
from cart.models import Order, ProductsInOrder
from crm_integration.actions.bitrix import BaseBitrixAction


class CreateOrderAction(BaseBitrixAction):
    get_user_webhook_url = getattr(settings, "GET_USER_WEBHOOK_URL", None)
    lead_add_webhook_url = getattr(settings, "LEAD_ADD_WEBHOOK_URL", None)
    lead_update_webhook_url = getattr(settings, "LEAD_UPDATE_WEBHOOK_URL", None)

    def execute(self, data):
        order_id = data.get("id")
        order = Order.objects.get(pk=order_id)

        domain = data.get("domain")
        if not any((order, domain)):
            raise ValueError(
                f"the 'data' object must include both keys: 'order' and 'domain'"
            )

        asyncio.run(self.create_lead_for_order(order, domain))
        logger.info("Order created in CRM successfully!")

    async def _get_user(self, email: str) -> dict:
        url = f"{self.get_user_webhook_url}/user.get.json"
        resp = await self.post_response(url, params={"EMAIL": email})
        user_data = resp[0].get(
            "result",
            [
                {},
            ],
        )[0]

        return user_data

    async def get_default_lead_user(self):
        default_lead_user_email = getattr(settings, "DEFAULT_LEAD_USER_EMAIL", None)
        result = await self._get_user(email=default_lead_user_email)
        return result

    async def create_lead_for_order(self, order: Order, domain: str):
        lead_user_id = (await self.get_default_lead_user()).get("ID")
        try:
            city = await City.objects.aget(domain=domain)
        except City.DoesNotExist:
            raise ValueError(f"City with provided 'domain'='{domain}' not found.")

        city_name = getattr(city, "name", None)

        ordered_prods = await sync_to_async(list)(
            ProductsInOrder.objects.filter(order=order)
        )
        comment_lines = []
        for op in ordered_prods:
            product = await sync_to_async(
                lambda: op.product
            )()
            comment_lines.append(
                f"{product.title}\n\tКоличество: {op.quantity}\n\tЦена: {float(op.price)}"
            )
        comment = "\n".join(comment_lines)

        customer = await sync_to_async(lambda: order.customer)()
        get_name = lambda fn, ln: f"{fn} {ln}".strip()
        customer_name = (
            get_name(customer.first_name, customer.last_name)
            if customer.first_name and customer.last_name
            else get_name(order.receiver_first_name, order.receiver_last_name)
        )
        phone = (
            order.receiver_phone
            if customer.phone is None
            else customer.phone
        )

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

        result, status = await self.add_lead(lead_data)
        if not 200 <= status < 400:
            logger.error(f"Order Lead creation failed, response data: {result}")

        return result

    async def add_lead(self, lead_data: dict):
        url = f"{self.lead_add_webhook_url}/crm.lead.add.json"
        return await self.post_response(url, lead_data)

    async def update_lead(self, id: int, fields: dict):
        url = f"{self.lead_update_webhook_url}/crm.lead.update.json"
        json = {
            "id": id,
            "fields": fields,
        }
        return await self.post_response(url, data=json)
