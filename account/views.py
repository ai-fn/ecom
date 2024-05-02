from django.conf import settings

from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from api.mixins import SendVirifyEmailMixin
from api.serializers.city import CitySerializer
from api.serializers.user import UserDetailInfoSerializer, UserRegistrationSerializer
from api.permissions import OwnerOrIsAdmin

from account.models import City, CustomUser

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=["Account"],
    description="Регистрация пользователя",
    summary="Регистрация пользователя",
    responses={200: UserRegistrationSerializer()},
    examples=[
        OpenApiExample(
            response_only=True,
            name="Register Responce Example",
            value={
                "username": "root_user",
                "email": "user@example.com",
                "password": "q3465rwdseewq3411_&3q",
                "phone": "+79983543246",
            },
        ),
        OpenApiExample(
            request_only=True,
            name="Register Request Example",
            value={
                "username": "root_user",
                "email": "user@example.com",
                "password": "q3465rwdseewq3411_&3q",
                "phone": "+79983543246",
            },
        ),
    ],
)
class Register(GenericAPIView, SendVirifyEmailMixin):

    serializer_class = UserRegistrationSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            new_user = serializer.create(serializer.validated_data)
            self._send_confirm_email(request, new_user, new_user.email)

            if new_user.phone:
                self._send_verify_sms()

            return Response(
                {"message": "Successfullly signed up"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=["Account"],
    description="Подтверждение регистрации пользователя",
    summary="Подтверждение регистрации пользователя",
)
class EmailVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        examples=[
            OpenApiExample(
                name="Response Example",
                value={
                    "message": "User 'dummy_user' email successfully verified"
                },
                response_only=True
            )
        ]
    )
    def get(self, request, uid64, token):
        user = self.get_user(request.user, uid64)
        if user is not None and settings.DEFAULT_TOKEN_GENERATOR.check_token(
            user, token
        ):
            user.is_active = True
            user.email_confirmed = True
            user.save()
            return Response(
                {"message": f"User {user} email successfully verified"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Confirmation code expired, request a new code"}, status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_user(user, uid64):
        try:
            uid = urlsafe_base64_decode(uid64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        return user


@extend_schema(tags=["Account"])
class AccountInfoViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, SendVirifyEmailMixin
):
    serializer_class = UserDetailInfoSerializer
    permission_classes = [OwnerOrIsAdmin]
    queryset = CustomUser.objects.all()

    @extend_schema(
        description="Получение подробной информации о пользователе",
        summary="Получение информации о пользователе",
        examples=[
            OpenApiExample(
                name="Пример ответа на получение информации",
                response_only=True,
                value={
                    'first_name': 'John',
                    'last_name': 'Conors',
                    'middle_name': 'James',
                    'email': 'dummy_user@gmail.com',
                    'phone': '+79933519856',
                    'region': 'Воронежская область',
                    'district': 'Лискинский район',
                    "city_name": "Воронеж",
                    'street': 'ул. Садовая',
                    'house': '101Б',
                    'is_active': True,
                }
            )
        ]
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
                    'first_name': 'John',
                    'last_name': 'Conors', 
                }
            ),
            OpenApiExample(
                name="Пример ответа на частичное изменение",
                response_only=True,
                value={
                    'first_name': 'John',
                    'last_name': 'Conors', 
                    'middle_name': 'James',
                    'email': 'dummy_user@gmail.com',
                    'phone': '+79933519856',
                    'region': 'Воронежская область',
                    'district': 'Лискинский район',
                    "city_name": "Воронеж",
                    'street': 'ул. Садовая',
                    'house': '101Б',
                    'is_active': True,
                }
            )
        ]
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
                return Response({"message": _("prodided email address already confirmed")})
            
            user.email = address
            user.email_confirmed = False
            user.save()
            return self._send_confirm_email(request, user, address)

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['Account']
    )
    @action(detail=False, methods=['get'])
    def all_cities(request, *args, **kwargs):
        return Response(
            {"results": CitySerializer(City.objects.all(), many=True).data}, status=status.HTTP_200_OK
        )
