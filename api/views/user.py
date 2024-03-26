from api.serializers.user import UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['api'],
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
            }
        ),
        OpenApiExample(
            request_only=True,
            name="Register Request Example",
            value={
                "username": "root_user",
                "email": "user@example.com",
                "password": "q3465rwdseewq3411_&3q",
                "phone": "+79983543246",
            }
        )
    ]
)
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Разрешить доступ неавторизованным пользователям
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
