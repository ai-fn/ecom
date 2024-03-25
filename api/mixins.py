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

    def validate_address(self, value):
        geolocator = Nominatim(user_agent="my_geocoder")
        location = geolocator.geocode(value)
        if not location:
            raise serializers.ValidationError("Invalid address. Please provide a valid address with city, region, street, and house number.")
        
        return value
