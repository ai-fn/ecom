from account.models import CustomUser
from account.actions import SendCodeToEmailAction

from django.conf import settings
from django.core.cache import cache

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny

from api.serializers._jwt import MyTokenObtainPairSerializer
from api.serializers.confirm_code import ConfirmCodeSerializer

from drf_spectacular.utils import OpenApiExample, OpenApiParameter
from drf_spectacular.utils import extend_schema, extend_schema_view

code_lifetime = int(getattr(settings, "CONFIRM_CODE_LIFE_TIME", 60 * 30))
remaining_time = int(getattr(settings, "CONFIRM_CODE_REMAINING_TIME", 60 * 2))


@extend_schema_view(
    send_code=extend_schema(
        tags=["Account"],
        description=f"Отпарвка сообщения c кодом. Кэширование запроса на {code_lifetime} секунд.",
        summary="Отпарвка сообщения c кодом",
        examples=[
            OpenApiExample(
                name="Пример запроса (Email)",
                value={"email": "example@gmail.com"},
                request_only=True,
            ),
            OpenApiExample(
                name="Пример запроса (Phone)",
                value={"phone": "+79889889898"},
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example", value={"success": True}, response_only=True
            ),
        ],
    ),
    verify_code=extend_schema(
        tags=["Account"],
        description="Проверка кода подтверждения.",
        summary="Проверка кода подтверждения",
        examples=[
            OpenApiExample(
                name="Пример запроса", value={"code": "4378"}, request_only=True
            ),
            OpenApiExample(
                name="Response Example",
                value={
                    "message": "User successfully activated",
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxODk3NjU4NCwiaWF0IjoxNzE3NjgwNTg0LCJqdGkiOiIxMWU1NjFhMDU1NGY0ZTYyYWYwODdlZjI1ODdiYTBlOCIsInVzZXJfaWQiOjcsInVzZXJuYW1lIjoiKzc5ODg5ODg5ODk4In0.XaVP2bCuzRW2hk_zcZbdObIUHpi6ynu4uDsT66A1OLY",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE3NjgwODg0LCJpYXQiOjE3MTc2ODA1ODQsImp0aSI6IjE4NzRmZDliMzdmNTRiOWZiY2YxNzI3ZGE1OGNhN2E5IiwidXNlcl9pZCI6NywidXNlcm5hbWUiOiIrNzk4ODk4ODk4OTgifQ.4y5LOdHwHtfrspvzbAWH9DUwqhJxUZBuByv3rmQaFZ4",
                    "access_expired_at": 1717680884.4001374,
                    "refresh_expired_at": 1718976584.4001443,
                },
                response_only=True,
            ),
        ],
    ),
)
class ConfirmCodesViewSet(GenericViewSet):
    send_code_action = SendCodeToEmailAction()
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ConfirmCodeSerializer

    @action(detail=False, methods=["post"], url_path="send-code")
    def send_code(self, request, *args, **kwargs) -> Response:
        return self.send_code_action.execute(request)

    @action(detail=False, methods=["post"], url_path="verify_code")
    def verify_code(self, request, *args, **kwargs) -> Response:

        serializer = ConfirmCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cache_salt = request.META.get("REMOTE_ADDR")
        user, message = self.send_code_action.verify(serializer.validated_data["code"], cache_salt)
        data = {"message": message}
        if user:
            serialized_tokens = MyTokenObtainPairSerializer.get_response(user)
            data.update(**serialized_tokens)
            return Response(data, status=status.HTTP_200_OK)

        return Response(data, status=status.HTTP_400_BAD_REQUEST)
