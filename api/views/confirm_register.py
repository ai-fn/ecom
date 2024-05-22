from datetime import datetime, timedelta
import time
from drf_spectacular.utils import OpenApiExample
import requests
import random as rd

from string import digits

from django.conf import settings
from django.core.cache import cache

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from ..serializers._jwt import MyTokenObtainPairSerializer
from ..serializers.phone import PhoneSerializer
from ..serializers.confirm_code import ConfirmCodeSerializer
from account.models import CustomUser
from drf_spectacular.utils import extend_schema

code_lifetime = int(getattr(settings, "CONFIRM_CODE_LIFE_TIME", 60*30))
remaining_time = int(getattr(settings, "CONFIRM_CODE_REMAINING_TIME", 60*2))


@extend_schema(
    tags=["Account"],
    description=f"Отпарвка СМС сообщения. Кэширование запроса на {code_lifetime} секунд.",
    summary="Отпарвка СМС сообщения",
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

        bot_token = settings.TG_BOT_TOKEN
        send_to_telegram = settings.SEND_TO_TELEGRAM
        chat_id = settings.CHAT_ID

        serializer_instance = self.serializer_class(data=request.data)
        serializer_instance.is_valid(raise_exception=True)
        phone_number: str = serializer_instance.data.get("phone_number")

        if not phone_number:
            return Response(
                {"error": "Missing phone number"}, status=status.HTTP_400_BAD_REQUEST
            )

        cache_prefix = getattr(settings, "SMS_CACHE_PREFIX", "SMS_CACHE")
        cache_key = f"{cache_prefix}_{phone_number}"
        cached_data = cache.get(cache_key)

        if cached_data:
            ren_time = cached_data.get("expiration_time") - time.time()
            if ren_time >= 0:
                return Response(
                    {
                        "message": f"Please wait. Time remaining: {int(ren_time)} seconds"
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        code = "".join(rd.choices(digits, k=4))
        message = f"Ваш код: {code}. Никому не сообщайте его!"
        api_key = getattr(settings, "SMS_RU_TOKEN", "default")

        try:
            sms_link = "https://sms.ru/sms/send"
            sms_params = {
                "api_id": api_key,
                "to": phone_number,
                "msg": message,
                "json": 1,  # to receive response in JSON format
            }

            tg_link = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            tg_params = {
                "chat_id": chat_id,
                "text": message,
                "json": 1,  # to receive response in JSON format
            }

            if not send_to_telegram:
                response = requests.get(sms_link, params=sms_params)
            else:
                response = requests.post(tg_link, params=tg_params)

            response_data = response.json()

            if response_data.get("status") == "OK" or response_data.get("ok"):
                cache.set(
                    cache_key,
                    {
                        "expiration_time": time.time() + remaining_time,
                        "code": code,
                    },
                    timeout=code_lifetime,
                )
                return Response({"success": True}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "error": (
                            response_data.get(
                                "status_text",
                                "%s: %s"
                                % (
                                    response_data.get("error_code"),
                                    response_data.get("description"),
                                ),
                            )
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Account"],
    description="Проверка кода подтверждения.",
    summary="Проверка кода подтверждения",
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
            phone=phone_number, defaults={"username": phone_number, "is_active": True}
        )

        if created:
            user.set_password(phone_number)
            user.save()

        serialized_tokens = MyTokenObtainPairSerializer().validate(
            {"username": user.username, "password": user.phone}
        )
        return Response(
            {"message": "User successfully activated", **serialized_tokens},
            status=status.HTTP_200_OK,
        )
