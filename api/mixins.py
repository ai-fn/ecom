from decimal import Decimal
import time
from loguru import logger
from typing import Any, Dict
from django.conf import settings
import phonenumbers

from geopy.geocoders import Nominatim

from rest_framework import serializers

from shop.models import Price


class ValidatePhoneNumberMixin:

    def validate_phone_number(self, value):
        phone_number = value
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise serializers.ValidationError("Invalid phone number.")

        return value


class ValidateAddressMixin:

    def validate(self, data):

        data = super().validate(data)
        address_fields = ("region", "district", "city_name", "house", "street")

        if any([field in address_fields for field in data]):

            # Получаем поля адреса из тела запроса, если есть, иначе получаем из объекта пользователя
            address_values = [data.get(field, getattr(self.context["request"].user, field, "")) or "" for field in address_fields]
            address = ", ".join(address_values[::-1])

            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(address)

            if not location:
                raise serializers.ValidationError(f"Получено: {address}. Неверный адрес. Пожалуйста, укажите действительный адрес с указанием города, области, улицы и номера дома.")
            
            logger.info(f"Найден адрес: {location.address}")
        return data


class TokenExpiredTimeMixin:

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        data['access_expired_at'] = time.time() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        data['refresh_expired_at'] = time.time() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        return data


class CityPricesMixin:

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {})
        kwargs['context']["city_domain"] = getattr(self, "domain", "")
        kwargs['context']["request"] = getattr(self, "request", "")
        return super().get_serializer(*args, **kwargs)


class SerializerGetPricesMixin:

    def get_city_price(self, obj) -> Decimal | None:
        city_domain = self.context.get('city_domain')
        if city_domain:
            price = Price.objects.filter(city__domain=city_domain, product=obj).first()
            if price:
                return price.price
        return None

    def get_old_price(self, obj) -> Decimal | None:
        city_domain = self.context.get('city_domain')
        if city_domain:
            price = Price.objects.filter(city__domain=city_domain, product=obj).first()
            if price:
                return price.old_price
        return None
