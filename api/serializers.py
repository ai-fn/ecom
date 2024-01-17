from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.serializers import (
    CharField,
    HyperlinkedModelSerializer,
    ModelSerializer,
    Serializer,
)
from rest_framework import serializers

from account.models import City, CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

from shop.models import Characteristic, CharacteristicValue, Price, Product, Review, Setting


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "password"]

    def validate(self, data):
        user = CustomUser(**data)
        password = data.get("password")

        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_errors = serializers.as_serializer_error(e)
            raise exceptions.ValidationError(
                {"password": serializer_errors["non_field_errors"]}
            )

        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )

        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "description",
            "image",
            "slug",
            "created_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "name",
            "rating",
            "review",
            "created_at",
        ]


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = [
            "id",
            "name",
            "category",
        ]


class CharacteristicValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacteristicValue
        fields = [
            "id",
            "product",
            "characteristic",
            "value",
        ]


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = [
            "id",
            "product",
            "city",
            "price",
        ]


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            "id",
            "key",
            "type",
            "value",
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "domain",
        ]