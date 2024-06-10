from geopy.exc import GeocoderServiceError
from loguru import logger
from rest_framework.exceptions import ValidationError
from geopy.geocoders import Nominatim


class ValidateAddressMixin:

    def validate_address(self, address):

        def split_address(address):
            parts = set()
            for part in address.split(','):
                parts.update(part.strip().split())
            return parts

        if not address:
            return ValidationError("Адрес не может быть пустым.")
        
        try:
            geolocator = Nominatim(user_agent="my_geocoder")
            locations = geolocator.geocode(address, exactly_one=False)
            if not locations:
                raise ValidationError("Указан несуществующий адрес")
            
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
                raise ValidationError("Адрес найден, но значительно отличается от введенного.")

            logger.info(f"Найден адрес: {max_match_address}")
            return max_match_address
        
        except GeocoderServiceError as e:
            raise ValidationError(f"{str(e)}\nОшибка службы геокодирования. Пожалуйста, повторите попытку позже.")
