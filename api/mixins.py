import time
from loguru import logger
from typing import Any, Dict
from django.conf import settings
import phonenumbers

from geopy.geocoders import Nominatim

from rest_framework import serializers


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

        address = ", ".join([data["region"], data["district"], data["city_name"], data["house"], data["street"]][::-1])

        geolocator = Nominatim(user_agent="my_geocoder")
        location = geolocator.geocode(address)

        if not location:
            raise serializers.ValidationError("Неверный адрес. Пожалуйста, укажите действительный адрес с указанием города, области, улицы и номера дома.")
        
        logger.info(f"Найден адрес: {location.address}")
        return data


class TokenExpiredTimeMixin:

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        data['access_expired_at'] = time.time() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        data['refresh_expired_at'] = time.time() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        return data
