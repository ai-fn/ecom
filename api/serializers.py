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

from account.models import City, CityGroup, CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from cart.models import Order, ProductsInOrder

from shop.models import (
    Category,
    CategoryMetaData,
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
    ProductImage,
    Review,
    Setting,
)


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


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryMetaData
        fields = ["title", "description"]


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)
    image_url = (
        serializers.SerializerMethodField()
    )  # Добавляем поле для URL изображения

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "children",
            "category_meta",
            "icon",
            "image_url",
        ]

    def get_children(self, obj):
        if obj.is_leaf_node():
            return None
        return CategorySerializer(obj.get_children(), many=True).data

    def get_image_url(self, obj):
        if obj.image:  # Проверяем, есть ли у категории изображение
            return obj.image.url  # Возвращаем URL изображения
        return None  # Если изображения нет, возвращаем None


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


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
    characteristic_name = serializers.CharField(source="characteristic.name")

    class Meta:
        model = CharacteristicValue
        fields = [
            "id",
            "characteristic_name",
            "value",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductCatalogSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True,)

    city_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, read_only=True
    )
    old_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "brand",
            "image",
            "slug",
            "city_price",
            "old_price",
            "images",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True, source="images")

    city_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, read_only=True
    )
    old_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, read_only=True
    )
    characteristic_values = CharacteristicValueSerializer(many=True, read_only=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "brand",
            "description",
            "image",
            "slug",
            "created_at",
            "city_price",
            "old_price",
            "characteristic_values",
            "images",
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
            "value_string",
            "value_boolean",
            "value_number",
            "predefined_key",
            "custom_key",
        ]

    def validate(self, data):
        if not data.get("predefined_key") and not data.get("custom_key"):
            raise serializers.ValidationError(
                "Необходимо указать либо предопределенный ключ, либо пользовательский ключ."
            )
        if data.get("predefined_key") and data.get("custom_key"):
            raise serializers.ValidationError(
                "Укажите только один ключ: либо предопределенный, либо пользовательский."
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["value"] = instance.get_value()
        return representation


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "domain",
        ]


class CityGroupSerializer(serializers.ModelSerializer):
    main_city = CitySerializer(read_only=True)
    cities = CitySerializer(many=True, read_only=True)

    class Meta:
        model = CityGroup
        fields = [
            "id",
            "name",
            "main_city",
            "cities",
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "category_meta"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "created_at",
        ]


class ProductsInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsInOrder
        fields = [
            "id",
            "order",
            "product",
            "quantity",
            "created_at",
        ]
