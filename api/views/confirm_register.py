import requests
import random as rd

from string import digits

from django.conf import settings
from django.core.cache import cache

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from ..serializers._jwt import TokenObtainPairSerializer
from ..serializers.phone import PhoneSerializer
from ..serializers.confirm_code import ConfirmCodeSerializer
from account.models import CustomUser


CACHE_KEY_PREFIX = "CONFIRMATION_CODE"

from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=['Account']
)
class SendConfirmSMS(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer

    def post(self, request):
        """
        Отправляет SMS сообщение через сервис SMS.ru.

        Args:
            phone_number (str): Номер телефона в международном формате.
        """
        if request.method == "POST":
            phone_number = request.data.get("phone_number")
            serializer = self.serializer_class(data={'phone_number': phone_number})
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            code = "".join(rd.choices(digits, k=4))
            message = "Ваш код: %s" % code
            
            cache.set(key=code, value=phone_number, timeout=settings.CONFIRM_CODE_LIFE_TIME)
            
            msg = message.split(" ")
            api_url = f"https://sms.ru/sms/send?api_id={settings.SMS_RU_TOKEN}&to={phone_number}&msg={'+'.join(msg)}&json=1"
        
            try:
                response = requests.get(api_url)
                response_data = response.json()
                if not response_data["status"] == "OK":
                    return Response({'message': f"Ошибка отправки сообщения: {response_data.get('status_text')}"}, status=status.HTTP_400_BAD_REQUEST)

            except requests.exceptions.RequestException as e:
                return Response({'message': f"Ошибка соединения с SMS.ru: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Confirmation code successfuly sent'}, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Account']
)
class VerifyConfirmCode(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmCodeSerializer

    def post(self, request):

        phone_number = request.data.get('phone_number')
        phone_serializer = PhoneSerializer(data={'phone_number': phone_number})

        if not phone_serializer.is_valid():
            return Response({"message": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

        code = request.data.get('code')
        
        serializer = self.serializer_class(data={'code': code})
        phone_number = cache.get(code)
        
        if not serializer.is_valid() or not phone_number:
            return Response({'message': 'Incorrect confirmation code'}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = CustomUser.objects.get_or_create(phone_number=phone_number)

        user.is_active = True
        user.save()
        serialized_tokens = TokenObtainPairSerializer.get_token(user)
        return Response({'message': "User successfully activated", **serialized_tokens}, status=status.HTTP_200_OK)
