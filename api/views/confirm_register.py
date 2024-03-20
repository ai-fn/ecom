from drf_spectacular.utils import OpenApiExample
from datetime import datetime, timedelta
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
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=['Account'],
    description="Отпарвка СМС сообщения. Кэширование запроса на 60 секунд.",
    summary="Отпарвка СМС сообщения",
    responses=[{"409": "CONFLICT"}, {"200": "OK"}, {"500": "INTERNAL SERVER ERROR"}, {"400": "BAD REQUEST"}],
    examples=[
        OpenApiExample(
            name="Request Example",
            value={
                "phone_number": "+79889889898"
            }
        )
    ]
)
class SendSMSView(GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer

    def post(self, request):
        """
        Отправляет SMS сообщение через сервис SMS.ru.

        Args:
            phone_number (str): Номер телефона в международном формате.
        """
        api_key = settings.SMS_RU_TOKEN
        serializer_instance = self.serializer_class(data=request.data)
        serializer_instance.is_valid(raise_exception=True)
        phone_number = serializer_instance.data.get("phone_number")

        if not phone_number:
            return Response({'error': 'Missing phone number'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_prefix = getattr(settings, "SMS_CACHE_PREFIX", "SMS_CACHE")
        cache_key = f'{cache_prefix}_{phone_number}'
        cached_data = cache.get(cache_key)

        if cached_data:
            remaining_time = cached_data.get('expiration_time') - datetime.now()
            if remaining_time.total_seconds() > 0:
                return Response({'message': f'Please wait. Time remaining: {int(remaining_time.total_seconds())} seconds'}, status=status.HTTP_409_CONFLICT)

        message = "".join(rd.choices(digits, k=4))

        try:
            response = requests.get('https://sms.ru/sms/send', params={
                'api_id': api_key,
                'to': phone_number,
                'msg': message,
                'json': 1  # to receive response in JSON format
            })
            response_data = response.json()

            if response_data['status'] == 'OK':
                cache.set(cache_key, {'expiration_time': datetime.now() + timedelta(seconds=60), 'message': message}, timeout=None)  # Cache for 60 seconds
                return Response({'success': True}, status=status.HTTP_200_OK)
            else:
                return Response({'error': response_data['status_text']}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
