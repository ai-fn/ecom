from typing import Any, Dict
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from api.mixins import TokenExpiredTimeMixin


class MyTokenObtainPairSerializer(TokenExpiredTimeMixin, TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username
        return token
    
    @classmethod
    def get_response(cls, user):
        token = cls.get_token(user)
        token["username"] = user.username
        
        data = {"refresh": str(token), "access": str(token.access_token)}
        data = cls._set_time_fields(data)
        return data


class MyTokenRefreshSerializer(TokenExpiredTimeMixin, TokenRefreshSerializer):
    pass


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
