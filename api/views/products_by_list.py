from django.db.models import F

from rest_framework.generics import GenericAPIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from api.serializers import ProductCatalogSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from shop.models import Product
from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE
from api.mixins import AnnotateProductMixin


@extend_schema(tags=["Shop"])
class ProductsById(GenericAPIView, AnnotateProductMixin):

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    pagination_class = PageNumberPagination
    queryset = Product.objects.all()

    @extend_schema(
        description="Получение информации о товарах по массиву с id товаров",
        summary="Получение информации о товарах по массиву с id товаров",
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для получения цены товара",
            )
        ],
        examples=[
            OpenApiExample(
                name="Request Products Example",
                value={
                    "ids_list": [
                        5572,
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Domain Provided Example",
                value=UNAUTHORIZED_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        self.domain = request.query_params.get("city_domain")
        ids_list = request.data.get("ids_list")

        if not ids_list:
            return Response(
                {"error": "ID's list is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.queryset.filter(pk__in=ids_list)

        page = self.paginate_queryset(queryset)
        if page is not None:
            queryset = queryset.filter(id__in=map(lambda x: x.id, page))
            serializer = self.get_serializer(self.annotate_queryset(queryset), many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.annotate_queryset(queryset), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
