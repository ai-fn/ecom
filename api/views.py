from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from account.models import City

from api.serializers import (
    CharacteristicSerializer,
    CharacteristicValueSerializer,
    CitySerializer,
    MyTokenObtainPairSerializer,
    PriceSerializer,
    ProductSerializer,
    ReviewSerializer,
    SettingSerializer,
)
from rest_framework import permissions, status, viewsets

from shop.models import (
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
    Review,
    Setting,
)


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Возвращает пользователей МойСклад
    """

    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReviewViewSet(viewsets.ModelViewSet):
    """Возвращает отзывы

    Args:
        viewsets (_type_): _description_
    """

    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]


class CharacteristicViewSet(viewsets.ModelViewSet):
    """Возвращает характеристики продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = Characteristic.objects.all().order_by("-created_at")
    serializer_class = CharacteristicSerializer
    permission_classes = [permissions.IsAuthenticated]


class CharacteristicValueViewSet(viewsets.ModelViewSet):
    """Возвращает значение характеристик продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = CharacteristicValue.objects.all().order_by("-created_at")
    serializer_class = CharacteristicValueSerializer
    permission_classes = [permissions.IsAuthenticated]


class PriceViewSet(viewsets.ModelViewSet):
    """Возвращает цены

    Args:
        viewsets (_type_): _description_
    """

    queryset = Price.objects.all().order_by("-created_at")
    serializer_class = PriceSerializer
    permission_classes = [permissions.IsAuthenticated]


class SettingViewSet(viewsets.ModelViewSet):
    """Возвращает настройки

    Args:
        viewsets (_type_): _description_
    """

    queryset = Setting.objects.all().order_by("-created_at")
    serializer_class = SettingSerializer
    permission_classes = [permissions.IsAuthenticated]


class CityViewSet(viewsets.ModelViewSet):
    """Возвращает города

    Args:
        viewsets (_type_): _description_
    """

    queryset = City.objects.all().order_by("-created_at")
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]
