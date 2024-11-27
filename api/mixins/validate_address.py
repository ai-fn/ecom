from typing import Optional
from geopy.exc import GeocoderServiceError
from loguru import logger
from rest_framework.exceptions import ValidationError
from geopy.geocoders import Nominatim


class ValidateAddressMixin:
    """
    Mixin для валидации адреса с использованием сервиса геокодирования Geopy.

    Проверяет существование адреса, сравнивает введенный адрес с найденным и возвращает
    наиболее подходящий адрес.
    """

    def validate_address(self, address: str) -> Optional[str]:
        """
        Проверяет и валидирует адрес с помощью сервиса геокодирования.

        :param address: Введенный пользователем адрес.
        :type address: str
        :return: Найденный и проверенный адрес.
        :rtype: Optional[str]
        :raises ValidationError: Если адрес пустой, не найден или значительно отличается.
        """

        def split_address(address: str) -> set:
            """
            Разделяет адрес на отдельные части для сравнения.

            :param address: Адрес для разделения.
            :type address: str
            :return: Множество частей адреса.
            :rtype: set
            """
            parts = set()
            for part in address.split(","):
                parts.update(part.strip().split())
            return parts

        if not address:
            raise ValidationError("Адрес не может быть пустым.")

        try:
            geolocator = Nominatim(user_agent="my_geocoder")
            locations = geolocator.geocode(address, exactly_one=False)
            if not locations:
                raise ValidationError("Указан несуществующий адрес.")

            user_address_parts = split_address(address.lower())
            matches = {}

            for location in locations:
                found_address_parts = split_address(location.address.lower())
                common_parts = user_address_parts.intersection(found_address_parts)
                match_score = len(common_parts) / len(user_address_parts)
                matches[location.address] = match_score

            max_match_address = max(matches, key=matches.get)
            max_match_score = matches[max_match_address]

            if max_match_score < 0.8:
                raise ValidationError(
                    "Адрес найден, но значительно отличается от введенного."
                )

            logger.info(f"Найден адрес: {max_match_address}")
            return max_match_address

        except GeocoderServiceError as e:
            raise ValidationError(
                f"{str(e)}\nОшибка службы геокодирования. Пожалуйста, повторите попытку позже."
            )
