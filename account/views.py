from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from api.mixins import SendVerifyEmailMixin
from api.serializers.user import UserDetailInfoSerializer
from api.permissions import UserInfoPermission

from account.models import CustomUser

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample


RESPONSE_EXAMPLE = {
    "first_name": "Админ",
    "last_name": "Админов",
    "email": "parovozikdima@gmail.com",
    "middle_name": None,
    "phone": "+7(993)6746657",
    "address": None,
    "is_active": True,
    "email_confirmed": True,
}


@extend_schema(tags=["Account"])
@extend_schema_view(
    verify_email=extend_schema(
        description="Подтверждение почты",
        summary="Подтверждение почты",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={"message": "User 'dummy_user' email successfully verified"},
                response_only=True,
            ),
            OpenApiExample(
                name="Пример запроса",
                value={"code": "9999"},
                request_only=True,
            ),
        ],
    ),
    resend_verify_email=extend_schema(
        description="Отправить заново код подтверждения почты",
        summary="Отправить заново код подтверждения почты",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={
                    "message": "Message sent successfully",
                    "expiration_time": 1717680326.8678553,
                },
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получение подробной информации о пользователе",
        summary="Получение информации о пользователе",
        examples=[
            OpenApiExample(
                name="Пример ответа на получение информации",
                response_only=True,
                value=RESPONSE_EXAMPLE,
            )
        ],
    ),
    partial_update=extend_schema(
        description="Частичное изменение информации о пользователе",
        summary="Частичное изменение информации о пользователе",
        examples=[
            OpenApiExample(
                name="Пример запроса на частичное изменение",
                request_only=True,
                value={
                    "first_name": "John",
                    "last_name": "Conors",
                },
            ),
            OpenApiExample(
                name="Пример ответа на частичное изменение",
                response_only=True,
                value=RESPONSE_EXAMPLE,
            ),
        ],
    ),
)
class AccountInfoViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    SendVerifyEmailMixin,
):
    serializer_class = UserDetailInfoSerializer
    permission_classes = [UserInfoPermission, IsAuthenticated]
    queryset = CustomUser.objects.all()

    @action(methods=["post"], detail=False)
    def verify_email(self, request, *args, **kwargs):
        code = self.request.data.get("code")
        email = self.request.user.email

        if not (email or code):
            return Response({"error": "email and code both req"})

        cached_data = self._get_code(self.request.user.email)

        if not cached_data or code != cached_data.get("code"):
            return Response(
                {"error": "Confirmation code invalid or expired, request a new one"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.request.user.is_active = True
        self.request.user.email_confirmed = True
        self.request.user.save()
        return Response(
            {"message": f"User {self.request.user} email successfully verified"},
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False)
    @method_decorator(cache_page(SendVerifyEmailMixin._EMAIL_CACHE_REMAINING_TIME))
    def resend_verify_email(self, request, *args, **kwargs):
        email = request.user.email
        if not email:
            return Response(
                {"detail": "email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        return self._send_confirm_email(request, request.user, email)

    def retrieve(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.user.pk
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное изменение информации о пользователе.
        """
        self.kwargs["pk"] = request.user.pk

        response = super().partial_update(request, *args, **kwargs)
        if 200 <= response.status_code < 400 and "email" in request.data:
            user = self.get_object()
            return self._send_confirm_email(request, user, request.data["email"])

        return response
