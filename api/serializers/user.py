from api.serializers import ActiveModelSerializer

from account.models import CustomUser
from api.mixins import ValidateAddressMixin, ValidatePhoneNumberMixin

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

from api.serializers import ActiveModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserReviewSerializer(ActiveModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    middle_name = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model=CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "is_active",            
        ]


class UserSerializer(ActiveModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class UserCreateSerializer(ActiveModelSerializer):
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


class UserRegistrationSerializer(ActiveModelSerializer, ValidatePhoneNumberMixin):
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
        user.set_password(validated_data["phone"])
        user.save()
        return user


class UserDetailInfoSerializer(
    ValidateAddressMixin, ValidatePhoneNumberMixin, ActiveModelSerializer
):
    phone = serializers.CharField(max_length=16)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "middle_name",
            "phone",
            "address",
            "is_active",
            "email_confirmed"
        )
    
    def validate_email(self, value):
        if self.instance:
            if self.instance.email == value and self.instance.email_confirmed:
                raise ValidationError("Provided email already confirmed")

        return value
