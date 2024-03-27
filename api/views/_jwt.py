from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer

# Create your views here.
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['api']
)
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Возвращает access и refresh токены
    """
    serializer_class = MyTokenObtainPairSerializer

    @extend_schema(
        description="Получение пары JWT токенов",
        summary="Получение пары JWT токенов",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value={
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMjc0MDMzMCwiaWF0IjoxNzExNDQ0MzMwLCJqdGkiOiIxYTZhYzMxMTI4YTQ0YWQ3OWM5YjEzMzE3ODgxYjY1ZCIsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoicm9vdCJ9.3mJ4ajrhIU91GbVQleqe8B9uHczl8EMyCThDDgYAVq8",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNDQ0NjMwLCJpYXQiOjE3MTE0NDQzMzAsImp0aSI6IjUxOTJhZDNiMjE5MDQ2YzliZTZkMDg4MjA3M2E2MzJjIiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJyb290In0.-XIElOJ12iyphnmBmERG3mI0W8t2Oc4Vavb8mc1OYVM",
                    "access_expired_at": 1711444630.2152293,
                    "refresh_expired_at": 1721444630.2152293,
                }
            ),
            OpenApiExample(
                name="Request Example",
                request_only=True,
                value={
                    "username": "dummy-username",
                    "password": "dummy-password_qwerty12345"
                }
            )
        ]
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


@extend_schema(
    tags=['api']
)
class MyTokenRefreshView(TokenRefreshView):

    serializer_class = MyTokenRefreshSerializer

    @extend_schema(
        description="Обновление пары JWT токенов",
        summary="Обновление пары JWT токенов",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value={
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMjc0MDMzMCwiaWF0IjoxNzExNDQ0MzMwLCJqdGkiOiIxYTZhYzMxMTI4YTQ0YWQ3OWM5YjEzMzE3ODgxYjY1ZCIsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoicm9vdCJ9.3mJ4ajrhIU91GbVQleqe8B9uHczl8EMyCThDDgYAVq8",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNDQ0NjMwLCJpYXQiOjE3MTE0NDQzMzAsImp0aSI6IjUxOTJhZDNiMjE5MDQ2YzliZTZkMDg4MjA3M2E2MzJjIiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJyb290In0.-XIElOJ12iyphnmBmERG3mI0W8t2Oc4Vavb8mc1OYVM",
                    "access_expired_at": 1711444630.2152293,
                    "refresh_expired_at": 1721444630.2152293,
                }
            ),
            OpenApiExample(
                name="Request Example",
                request_only=True,
                value={
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMjc0MDMzMCwiaWF0IjoxNzExNDQ0MzMwLCJqdGkiOiIxYTZhYzMxMTI4YTQ0YWQ3OWM5YjEzMzE3ODgxYjY1ZCIsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoicm9vdCJ9",
                }
            )
        ]
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)
