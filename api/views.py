from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from account.models import City, CityGroup

from api.serializers import (
    CategoryDetailSerializer,
    CategoryMetaDataSerializer,
    CategorySerializer,
    CharacteristicSerializer,
    CharacteristicValueSerializer,
    CityGroupSerializer,
    CitySerializer,
    MyTokenObtainPairSerializer,
    OrderSerializer,
    PriceSerializer,
    ProductSerializer,
    ProductsInOrderSerializer,
    ReviewSerializer,
    SettingSerializer,
)
from rest_framework import permissions, status, viewsets
from cart.models import Order, ProductsInOrder

from shop.models import (
    Category,
    CategoryMetaData,
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
    Review,
    Setting,
)
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters


class ReadOnlyOrAdminPermission(permissions.BasePermission):
    """
    Разрешение, которое позволяет только чтение для всех пользователей, но полный доступ для администраторов.
    """

    def has_permission(self, request, view):
        # Проверка, является ли пользователь администратором
        if request.user and request.user.is_staff:
            return True

        # Проверка типа запроса: разрешить только запросы на чтение
        return request.method in permissions.SAFE_METHODS


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Возвращает пользователей МойСклад
    """

    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


class ReviewViewSet(viewsets.ModelViewSet):
    """Возвращает отзывы

    Args:
        viewsets (_type_): _description_
    """

    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


class CharacteristicViewSet(viewsets.ModelViewSet):
    """Возвращает характеристики продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = Characteristic.objects.all().order_by("-created_at")
    serializer_class = CharacteristicSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


class CharacteristicValueViewSet(viewsets.ModelViewSet):
    """Возвращает значение характеристик продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = CharacteristicValue.objects.all().order_by("-created_at")
    serializer_class = CharacteristicValueSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


class PriceFilter(FilterSet):
    class Meta:
        model = Price
        fields = ["city"]


class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all().order_by("-created_at")
    serializer_class = PriceSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PriceFilter


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
    permission_classes = [ReadOnlyOrAdminPermission]


class CityGroupViewSet(viewsets.ModelViewSet):
    """Возвращает группы городов

    Args:
        viewsets (_type_): _description_
    """

    queryset = CityGroup.objects.all().order_by("-created_at")
    serializer_class = CityGroupSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return CategoryDetailSerializer
        return super().get_serializer_class()


class CategoryMetaDataViewSet(viewsets.ModelViewSet):
    queryset = CategoryMetaData.objects.all().order_by("-created_at")
    serializer_class = CategoryMetaDataSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductsInOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductsInOrder.objects.all().order_by("-created_at")
    serializer_class = ProductsInOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
