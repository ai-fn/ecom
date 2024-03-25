from rest_framework import serializers
from api.mixins import ValidatePhoneNumberMixin

class PhoneSerializer(serializers.Serializer, ValidatePhoneNumberMixin):
    
    phone_number = serializers.CharField(max_length=16)
