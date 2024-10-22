from rest_framework import serializers
from api.mixins import ValidatePhoneNumberMixin


class PhoneSerializer(ValidatePhoneNumberMixin, serializers.Serializer):
    
    phone = serializers.CharField(max_length=16)
