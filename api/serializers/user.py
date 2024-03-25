from rest_framework import serializers

from account.models import CustomUser
from api.mixins import ValidateAddressMixin, ValidatePhoneNumberMixin

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


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


class UserRegistrationSerializer(serializers.ModelSerializer, ValidatePhoneNumberMixin):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    phone = serializers.CharField(max_length=16)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "phone")

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data["phone"],
        )
        return user


class UserDetailInfoSerializer(serializers.ModelSerializer, ValidatePhoneNumberMixin, ValidateAddressMixin):
    password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "password", "phone", "address")
