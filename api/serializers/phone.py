from rest_framework import serializers
from api.mixins import ValidatePhoneNumberMixin


class PhoneSerializer(ValidatePhoneNumberMixin, serializers.Serializer):
    
    phone = serializers.CharField(max_length=16)

    def validate_phone(self, value):
        self.phone_is_valid(value)
        return value
