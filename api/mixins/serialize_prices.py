from decimal import Decimal

from loguru import logger
from account.models import City
from shop.models import Price


class SerializerGetPricesMixin:

    def get_request_params(self) -> dict:
        request = self.context.get("request")
        return getattr(request, "query_params", {})

    def get_city_price(self, obj) -> Decimal | None:
        params = self.get_request_params()
        city_domain = params.get("city_domain") or params.get("domain")
        if city_domain:
            try:
                c = City.objects.get(domain=city_domain)
            except City.DoesNotExist:
                return None

            price = Price.objects.filter(city_group__cities=c, product=obj).first()
            if price:
                return price.price

        return None

    def get_old_price(self, obj) -> Decimal | None:
        params = self.get_request_params()
        city_domain = params.get("city_domain") or params.get("domain")
        if city_domain:
            try:
                c = City.objects.get(domain=city_domain)
            except City.DoesNotExist:
                return None

            price = Price.objects.filter(city_group__cities=c, product=obj).first()
            if price:
                return price.old_price

        return None
