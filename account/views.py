from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from api.mixins import SendVirifyEmailMixin
from api.serializers.user import UserDetailInfoSerializer
from api.permissions import OwnerOrIsAdmin

from account.models import CustomUser

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["Account"])
class AccountInfoViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    SendVirifyEmailMixin,
):
    serializer_class = UserDetailInfoSerializer
    permission_classes = [OwnerOrIsAdmin, IsAuthenticated]
    queryset = CustomUser.objects.all()

    @extend_schema(
        description="Подтверждение почты",
        summary="Подтверждение почты",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={"message": "User 'dummy_user' email successfully verified"},
                response_only=True,
            ),
            OpenApiExample(
                name="Request Example",
                value={"code": "9999"},
                request_only=True,
            ),
        ]
    )
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

    @extend_schema(
        description="Отправить заново код подтверждения почты",
        summary="Отправить заново код подтверждения почты",
        examples=[
            OpenApiExample(
                name="Request Example",
                value={},
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example", value={"code": "9999", "expiration_time": 1714730191.0360472}, response_only=True
            ),
        ],
    )
    @action(methods=["get"], detail=False)
    @method_decorator(cache_page(SendVirifyEmailMixin._EMAIL_CACHE_REMAINING_TIME))
    def resend_verify_email(self, request, *args, **kwargs):
        email = request.user.email
        if not email:
            return Response({"email is required"}, status=status.HTTP_400_BAD_REQUEST)

        return self._send_confirm_email(request, request.user, email)

    @extend_schema(
        description="Получение подробной информации о пользователе",
        summary="Получение информации о пользователе",
        examples=[
            OpenApiExample(
                name="Пример ответа на получение информации",
                response_only=True,
                value={
                    "first_name": "John",
                    "last_name": "Conors",
                    "middle_name": "James",
                    "email": "dummy_user@gmail.com",
                    "phone": "+79933519856",
                    "region": "Воронежская область",
                    "district": "Лискинский район",
                    "city_name": "Воронеж",
                    "street": "ул. Садовая",
                    "house": "101Б",
                    "is_active": True,
                },
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.user.pk
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
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
                value={
                    "first_name": "John",
                    "last_name": "Conors",
                    "middle_name": "James",
                    "email": "dummy_user@gmail.com",
                    "phone": "+79933519856",
                    "region": "Воронежская область",
                    "district": "Лискинский район",
                    "city_name": "Воронеж",
                    "street": "ул. Садовая",
                    "house": "101Б",
                    "is_active": True,
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Частичное изменение информации о пользователе.
        """
        self.kwargs["pk"] = request.user.pk
        user = self.get_object()

        if "email" in request.data:
            address = request.data.get("email")

            if address == user.email and user.email_confirmed:
                return Response(
                    {"message": _("prodided email address already confirmed")}
                )

            user.email = address
            user.email_confirmed = False
            user.save()
            return self._send_confirm_email(request, user, address)

        return super().partial_update(request, *args, **kwargs)
