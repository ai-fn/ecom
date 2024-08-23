from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer

from drf_spectacular.utils import  (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
)


JWT_RESPONSE_EXAMPLE = {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMjc0MDMzMCwiaWF0IjoxNzExNDQ0MzMwLCJqdGkiOiIxYTZhYzMxMTI4YTQ0YWQ3OWM5YjEzMzE3ODgxYjY1ZCIsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoicm9vdCJ9.3mJ4ajrhIU91GbVQleqe8B9uHczl8EMyCThDDgYAVq8",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNDQ0NjMwLCJpYXQiOjE3MTE0NDQzMzAsImp0aSI6IjUxOTJhZDNiMjE5MDQ2YzliZTZkMDg4MjA3M2E2MzJjIiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJyb290In0.-XIElOJ12iyphnmBmERG3mI0W8t2Oc4Vavb8mc1OYVM",
    "access_expired_at": 1711444630.2152293,
    "refresh_expired_at": 1721444630.2152293,
}
JWT_REFRESH_REQUEST_EXAMPLE = {
    "refresh": JWT_RESPONSE_EXAMPLE["refresh"],
}
JWT_REQUEST_EXAMPLE = {
    "username": "dummy-username",
    "password": "dummy-password_qwerty12345"
}

@extend_schema_view(
    post=extend_schema(
        description="Получение пары JWT токенов",
        summary="Получение пары JWT токенов",
        examples=[
            OpenApiExample(
                name="Пример ответа",
                response_only=True,
                value=JWT_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Пример запроса",
                request_only=True,
                value=JWT_REQUEST_EXAMPLE
            )
        ]
    ),
)
@extend_schema(
    tags=['api']
)
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Возвращает access и refresh токены
    """
    serializer_class = MyTokenObtainPairSerializer

@extend_schema_view(
    post=extend_schema(
        description="Обновление пары JWT токенов",
        summary="Обновление пары JWT токенов",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=JWT_RESPONSE_EXAMPLE
            ),
            OpenApiExample(
                name="Пример запроса",
                request_only=True,
                value=JWT_REFRESH_REQUEST_EXAMPLE,
            )
        ]
    )
)
@extend_schema(
    tags=['api']
)
class MyTokenRefreshView(TokenRefreshView):
    """
    Возвращает access и refresh токены
    """
    serializer_class = MyTokenRefreshSerializer
