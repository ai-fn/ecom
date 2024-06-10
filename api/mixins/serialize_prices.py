from decimal import Decimal

from loguru import logger
from account.models import City
from shop.models import Price


class SerializerGetPricesMixin:

    def get_city_price(self, obj) -> Decimal | None:
        city_domain = self.context.get("city_domain")
        if city_domain:
            try:
                c = City.objects.get(domain=city_domain)
            except City.DoesNotExist:
                logger.info(f"City with domain {city_domain} not found")
                return None

            price = Price.objects.filter(city_group__cities=c, product=obj).first()
            if price:
                return price.price

        return None

    def get_old_price(self, obj) -> Decimal | None:
        city_domain = self.context.get("city_domain")
        if city_domain:
            try:
                c = City.objects.get(domain=city_domain)
            except City.DoesNotExist:
                logger.info(f"City with domain {city_domain} not found")
                return None

            price = Price.objects.filter(city_group__cities=c, product=obj).first()
            if price:
                return price.old_price

        return None