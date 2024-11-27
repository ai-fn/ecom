from decimal import Decimal
from typing import Optional

from account.models import City
from shop.models import Price


class SerializerGetPricesMixin:
    """
    Mixin для получения цен текущего продукта, включая старую и текущую цены,
    на основе домена города из запроса.
    """

    def get_request_params(self) -> dict:
        """
        Получает параметры запроса из контекста сериализатора.

        :return: Словарь параметров запроса.
        :rtype: dict
        """
        request = self.context.get("request")
        return getattr(request, "query_params", {})

    def get_city_price(self, obj) -> Optional[Decimal]:
        """
        Возвращает текущую цену продукта для указанного домена города.

        :param obj: Объект продукта.
        :return: Цена продукта или None, если цена не найдена.
        :rtype: Optional[Decimal]
        """
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

    def get_old_price(self, obj) -> Optional[Decimal]:
        """
        Возвращает старую цену продукта для указанного домена города.

        :param obj: Объект продукта.
        :return: Старая цена продукта или None, если цена не найдена.
        :rtype: Optional[Decimal]
        """
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
