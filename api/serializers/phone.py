from api.serializers import ActiveModelSerializer
from api.mixins import ValidatePhoneNumberMixin
from rest_framework import serializers


class PhoneSerializer(serializers.Serializer, ValidatePhoneNumberMixin):
    
    phone_number = serializers.CharField(max_length=16)
