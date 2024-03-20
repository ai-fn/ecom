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

code_lifetime = int(settings.CONFIRM_CODE_LIFE_TIME)


@extend_schema(
    tags=["Account"],
    description=f"Отпарвка СМС сообщения. Кэширование запроса на {code_lifetime} секунд.",
    summary="Отпарвка СМС сообщения",
    responses=[
        {"409": "CONFLICT"},
        {"200": "OK"},
        {"500": "INTERNAL SERVER ERROR"},
        {"400": "BAD REQUEST"},
    ],
    examples=[
        OpenApiExample(name="Request Example", value={"phone_number": "+79889889898"})
    ],
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
            return Response(
                {"error": "Missing phone number"}, status=status.HTTP_400_BAD_REQUEST
            )

        cache_prefix = getattr(settings, "SMS_CACHE_PREFIX", "SMS_CACHE")
        cache_key = f"{cache_prefix}_{phone_number}"
        cached_data = cache.get(cache_key)

        if cached_data:
            remaining_time = cached_data.get("expiration_time") - datetime.now()
            if remaining_time.total_seconds() > 0:
                return Response(
                    {
                        "message": f"Please wait. Time remaining: {int(remaining_time.total_seconds())} seconds"
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        code = "".join(rd.choices(digits, k=4))
        message = f"Ваш код: {code}. Никому не сообщайте его!"
        print(message)

        # try:
        #     response = requests.get('https://sms.ru/sms/send', params={
        #         'api_id': api_key,
        #         'to': phone_number,
        #         'msg': message,
        #         'json': 1  # to receive response in JSON format
        #     })
        #     response_data = response.json()

        #     if response_data['status'] == 'OK':
        cache.set(
            cache_key,
            {
                "expiration_time": datetime.now() + timedelta(seconds=code_lifetime),
                "code": code,
            },
            timeout=code_lifetime,
        )  # Cache for 60 seconds
        #         return Response({'success': True}, status=status.HTTP_200_OK)
        #     else:
        #         return Response({'error': response_data['status_text']}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        return Response(status=status.HTTP_200_OK)


@extend_schema(
    tags=["Account"],
    description="Проверка кода подтверждения.",
    summary="Проверка кода подтверждения",
    responses=[
        {"409": "CONFLICT"},
        {"200": "OK"},
        {"500": "INTERNAL SERVER ERROR"},
        {"400": "BAD REQUEST"},
    ],
    examples=[
        OpenApiExample(
            name="Request Example",
            value={"phone_number": "+79889889898", "code": "4378"},
        )
    ],
)
class VerifyConfirmCode(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmCodeSerializer

    def post(self, request):

        phone_number = request.data.get("phone_number")
        phone_serializer = PhoneSerializer(data={"phone_number": phone_number})
        phone_serializer.is_valid(raise_exception=True)

        code = request.data.get("code")
        serializer = self.serializer_class(data={"code": code})
        serializer.is_valid(raise_exception=True)

        cached_key = f"{settings.SMS_CACHE_PREFIX}_{phone_number}"
        cached_data = cache.get(cached_key, {})
        cached_code = cached_data.get("code")

        if not cached_data or code != cached_code:
            return Response(
                {"message": "Invalid confirmation code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = CustomUser.objects.get_or_create(
            phone=phone_number, defaults={"username": phone_number}
        )

        if not user.is_active:
            user.is_active = True
            if created:
                user.set_password(phone_number)

            user.save()

        serialized_tokens = TokenObtainPairSerializer.get_token(user)
        return Response(
            {
                "message": "User successfully activated",
                "access": str(serialized_tokens.access_token),
                "refresh": str(serialized_tokens),
            },
            status=status.HTTP_200_OK,
        )
