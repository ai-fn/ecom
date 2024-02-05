from tempfile import NamedTemporaryFile
import pandas as pd
from django.shortcuts import render
from loguru import logger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from account.models import City, CityGroup
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q, Subquery, OuterRef
from rest_framework.views import APIView
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
    ProductCatalogSerializer,
    ProductDetailSerializer,
    ProductsInOrderSerializer,
    ReviewSerializer,
    SettingSerializer,
)
from rest_framework.decorators import action
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
from rest_framework.parsers import FileUploadParser
import openpyxl  # Для работы с xlsx
import csv  # Для работы с csv
from django.db import transaction
import magic  # Библиотека для определения MIME-типа файла
from pytils.translit import slugify



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
    Возвращает товары с учетом цены в заданном городе.
    """

    queryset = Product.objects.all().order_by("-created_at")
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductCatalogSerializer
        elif self.action == "productdetail":
            return ProductDetailSerializer
        return (
            ProductDetailSerializer  # Или какой-либо другой сериализатор по умолчанию
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для фильтрации цен",
            ),
            OpenApiParameter(
                name="price_gte",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Фильтр цены: больше или равно",
            ),
            OpenApiParameter(
                name="price_lte",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Фильтр цены: меньше или равно",
            ),
            OpenApiParameter(
                name="brand",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по бренду",
            ),
            OpenApiParameter(
                name="category",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по категории",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        city_domain = request.query_params.get("city_domain")
        price_lte = request.query_params.get("price_lte")
        price_gte = request.query_params.get("price_gte")
        brands = request.query_params.get("brand")
        category = request.query_params.get("category")

        if city_domain or price_gte or price_lte or brands:
            filter_conditions = Q()

            if city_domain:
                price_filter = Price.objects.filter(
                    product=OuterRef("pk"), city__domain=city_domain
                )

                if price_lte is not None:
                    price_filter = price_filter.filter(price__lte=price_lte)
                if price_gte is not None:
                    price_filter = price_filter.filter(price__gte=price_gte)

                filter_conditions &= Q(id__in=Subquery(price_filter.values("product")))

                self.queryset = self.queryset.annotate(
                    city_price=Subquery(price_filter.values("price")[:1]),
                    old_price=Subquery(price_filter.values("old_price")[:1]),
                )

            if brands:
                brands_list = brands.split(",")
                filter_conditions &= Q(brand__name__in=brands_list)

            if category:
                filter_conditions &= Q(category__slug=category) | Q(
                    additional_categories__slug=category
                )

            filtered_queryset = self.queryset.filter(filter_conditions)

            if not filtered_queryset.exists():
                return Response([])

            self.queryset = filtered_queryset

        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для получения цены товара",
            )
        ]
    )
    @action(detail=True, methods=["get"])
    def productdetail(self, request, pk=None):
        product = self.get_object()
        city_domain = request.query_params.get("city_domain")
        if city_domain:
            price_data = (
                Price.objects.filter(product=product, city__domain=city_domain)
                .values("price", "old_price")
                .first()
            )
            if price_data:
                product.city_price = price_data.get("price")
                product.old_price = price_data.get("old_price")

        serializer = self.get_serializer(product)
        return Response(serializer.data)


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
    permission_classes = [ReadOnlyOrAdminPermission]


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


class XlsxFileUploadView(APIView):
    parser_classes = [FileUploadParser]
    queryset = Product.objects.all()
    
    permission_classes = []
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Тип данных для импорта (PRODUCTS, BRANDS)",
            ),
        ]
    )
    def put(self, request, filename, format=None):
        file_obj = request.data["file"]
        upload_type = request.query_params.get(
            "type"
        )  # Получение параметра type из строки запроса

        # Проверка на поддерживаемые типы
        if upload_type not in ["PRODUCTS", "BRANDS"]:
            return Response(
                {"error": "Unsupported type parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if filename.endswith(".xlsx"):
            result = self.handle_xlsx_file(file_obj.file, upload_type)
        elif filename.endswith(".csv"):
            result = self.handle_csv_file(file_obj.file, upload_type)
        else:
            return Response(
                {"error": "Unsupported file format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if result is False:
            return Response(
                {"error": "Error processing file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


    def handle_xlsx_file(self, file_obj, upload_type):
        try:
            # Проверка MIME-типа файла для удостоверения, что это действительно Excel файл
            mime_type = magic.from_buffer(file_obj.read(2048), mime=True)
            file_obj.seek(0)  # Возвращаем указатель в начало файла после чтения

            # Создание временного файла для хранения содержимого .xlsx файла
            with NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
                tmp.write(file_obj.read())
                tmp.flush()
                tmp.seek(0)

                df = pd.read_excel(tmp.name, engine='openpyxl')
                try:
                    with transaction.atomic():
                        for _, row in df.iterrows():
                            category_path = row['CATEGORIES'].split(' | ')
                            category = None
                            for cat_name in category_path[0:-1]:  # Правильное исключение последнего элемента
                                if cat_name:  # Дополнительная проверка на непустое имя категории
                                    cat_slug = slugify(cat_name)
                                    if cat_slug:  # Проверяем, что slug не пустой
                                        parent_category = category
                                        category, created = Category.objects.get_or_create(
                                            name=cat_name,
                                            defaults={'slug': cat_slug, 'parent': parent_category}
                                        )
                                        # Обновляем parent только если категория была только что создана или если parent отличается
                                        if created or (category.parent != parent_category and parent_category is not None):
                                            category.parent = parent_category
                                            category.save()
                                    else:
                                        logger.error(f"Unable to create slug for category name '{cat_name}'. Skipping category creation.")
                                else:
                                    logger.error("Empty category name encountered. Skipping category creation.")

                            product_title = row['TITLE']
                            product_slug = slugify(product_title)
                            if product_slug:  # Проверяем, что slug продукта не пустой
                                product, created = Product.objects.get_or_create(
                                    title=product_title,
                                    defaults={
                                        'description': "row['DESCRIPTION']",
                                        'category': category,
                                        'slug': product_slug,
                                    }
                                )
                            else:
                                logger.error(f"Unable to create slug for product title '{product_title}'. Skipping product creation.")
                except Exception as err:
                    logger.error(err)
                
                # Определите список колонок, которые вы хотите игнорировать
                ignored_columns = ["TITLE", "DESCRIPTION", "IMAGES", "CATEGORIES", "SKU"]

                # Получите список колонок, которые не игнорируются
                columns_to_save = [col for col in df.columns if col not in ignored_columns]

                # Оставьте только нужные колонки в DataFrame
                df = df[columns_to_save]
                # Создание и сохранение характеристик в базе данных
                try:
                    characteristics_to_create = []
                    for index, row in df.iterrows():
                        for column_name in columns_to_save:
                            characteristic = Characteristic(name=column_name, category=None)
                            characteristics_to_create.append(characteristic)
                    # Вне цикла, создаем все объекты одним вызовом
                    Characteristic.objects.bulk_create(characteristics_to_create)
                except Exception as err:
                    logger.error(err)
                    pass
                
        except Exception as e:
            # logger.error("Error processing Excel file: " + str(e))
            return False
        
    def handle_csv_file(self, file, upload_type):
        try:
            # Чтение файла CSV в DataFrame
            df = pd.read_csv(file)
            # Логгирование структуры DataFrame
            logger.debug(df.head())
            
            with transaction.atomic():
                if upload_type == "PRODUCTS":
                    # Обработка данных о продуктах
                    for index, row in df.iterrows():
                        # Здесь ваша логика обработки для каждой строки данных о продуктах
                        pass
                elif upload_type == "BRANDS":
                    # Обработка данных о брендах
                    for index, row in df.iterrows():
                        # Здесь ваша логика обработки для каждой строки данных о брендах
                        pass
            return True
        except Exception as e:
            logger.error(e)
            # Логирование ошибки
            return False