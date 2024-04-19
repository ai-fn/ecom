from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from api.mixins import CityPricesMixin
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import PromoSerializer
from shop.models import Promo
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["Shop"],
    responses={200: PromoSerializer(many=True)},
    description="Retrieves promotions filtered by the domain of the city.",
)
class PromoViewSet(CityPricesMixin, ModelViewSet):

    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_permissions(self):
        if self.action == "active_promos":
            return [AllowAny()]

        return super().get_permissions()

    def get_queryset(self):
        # Получаем домен из параметров запроса
        self.domain = self.request.query_params.get("domain")
        if not self.domain:
            return Response([])

        # Возвращаем промоакции, связанные с найденными городами
        return self.queryset.filter(cities__domain=self.domain).distinct()

    @extend_schema(
        summary="Получение списка активных промо акций",
        description="Получение списка активных промо акций",
        responses={200: PromoSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение списка активных промо акций",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Promo 1",
                        "categories": [
                            {
                                "id": 1,
                                "name": "Category A",
                                "slug": "category-a",
                                "order": 1,
                                "parent": 1,
                                "children": 2,
                                "parents": ["Деке", "deke-1"],
                                "category_meta": [
                                    {
                                        "title": "dummy-title",
                                        "description": "dummy-description",
                                    }
                                ],
                                "category_meta_id": None,
                                "icon": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                                "image_url": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                                "is_visible": True,
                                "is_popular": True,
                            },
                        ],
                        "products": [
                            {
                                "title": "Product A",
                                "brand": 1,
                                "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                "slug": "product-a",
                                "city_price": 100.0,
                                "old_price": 120.0,
                                "images": [
                                    {
                                        "id": 1,
                                        "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                    },
                                    {
                                        "id": 2,
                                        "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                    },
                                ],
                                "category_slug": "category-a",
                            }
                        ],
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "cities": [
                            {
                                "name": "Воронеж",
                                "domain": "example.com",
                                "nominative_case": "Воронеж",
                                "genitive_case": "Воронежа",
                                "dative_case": "Воронежу",
                                "accusative_case": "Воронежем",
                                "instrumental_case": "Воронежем",
                                "prepositional_case": "Воронеже",
                            }
                        ],
                        "active_to": "2024-04-30",
                        "is_active": True,
                    },
                ],
            ),
        ],
    )
    @action(methods=["get"], detail=False)
    def active_promos(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().filter(is_active=True)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение списка промо акций",
        summary="Получение списка промо акций",
        parameters=[
            OpenApiParameter(
                name="domain",
                description="Домен города",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            )
        ],
        operation_id="api_promos_list",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение списка всех промо акций",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Promo 1",
                        "categories": [
                            {
                                "id": 1,
                                "name": "Category A",
                                "slug": "category-a",
                                "order": 1,
                                "parent": 1,
                                "children": 2,
                                "parents": ["Деке", "deke-1"],
                                "category_meta": [
                                    {
                                        "title": "dummy-title",
                                        "description": "dummy-description",
                                    }
                                ],
                                "category_meta_id": None,
                                "icon": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                                "image_url": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                                "is_visible": True,
                                "is_popular": True,
                            },
                        ],
                        "products": [
                            {
                                "title": "Product A",
                                "brand": 1,
                                "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                "slug": "product-a",
                                "city_price": 100.0,
                                "old_price": 120.0,
                                "images": [
                                    {
                                        "id": 1,
                                        "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                    },
                                    {
                                        "id": 2,
                                        "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                    },
                                ],
                                "category_slug": "category-a",
                            }
                        ],
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "cities": [
                            {
                                "name": "Воронеж",
                                "domain": "example.com",
                                "nominative_case": "Воронеж",
                                "genitive_case": "Воронежа",
                                "dative_case": "Воронежу",
                                "accusative_case": "Воронежем",
                                "instrumental_case": "Воронежем",
                                "prepositional_case": "Воронеже",
                            }
                        ],
                        "active_to": "2024-04-30",
                        "is_active": True,
                    },
                ],
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение промо акции по уникальному идентификатору",
        summary="Получение промо акции по уникальному идентификатору",
        parameters=[
            OpenApiParameter(
                name="domain",
                description="Домен города",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            )
        ],
        operation_id="api_promos_retrieve",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение промо акции",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Promo 1",
                    "categories": [
                        {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 1,
                            "children": 2,
                            "parents": ["Деке", "deke-1"],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description",
                                }
                            ],
                            "category_meta_id": None,
                            "icon": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "image_url": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "is_visible": True,
                            "is_popular": True,
                        },
                    ],
                    "products": [
                        {
                            "title": "Product A",
                            "brand": 1,
                            "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            "slug": "product-a",
                            "city_price": 100.0,
                            "old_price": 120.0,
                            "images": [
                                {
                                    "id": 1,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                                {
                                    "id": 2,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                            ],
                            "category_slug": "category-a",
                        }
                    ],
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "cities": [
                        {
                            "name": "Воронеж",
                            "domain": "example.com",
                            "nominative_case": "Воронеж",
                            "genitive_case": "Воронежа",
                            "dative_case": "Воронежу",
                            "accusative_case": "Воронежем",
                            "instrumental_case": "Воронежем",
                            "prepositional_case": "Воронеже",
                        }
                    ],
                    "active_to": "2024-04-30",
                    "is_active": True,
                },
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создание промо акции",
        summary="Создание промо акции",
        parameters=[
            OpenApiParameter(
                name="domain",
                description="Домен города",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            )
        ],
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на создание промо акции",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Promo 1",
                    "categories": [
                        {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 1,
                            "children": 2,
                            "parents": ["Деке", "deke-1"],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description",
                                }
                            ],
                            "category_meta_id": None,
                            "icon": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "image_url": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "is_visible": True,
                            "is_popular": True,
                        },
                    ],
                    "products": [
                        {
                            "title": "Product A",
                            "brand": 1,
                            "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            "slug": "product-a",
                            "city_price": 100.0,
                            "old_price": 120.0,
                            "images": [
                                {
                                    "id": 1,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                                {
                                    "id": 2,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                            ],
                            "category_slug": "category-a",
                        }
                    ],
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "cities": [
                        {
                            "name": "Воронеж",
                            "domain": "example.com",
                            "nominative_case": "Воронеж",
                            "genitive_case": "Воронежа",
                            "dative_case": "Воронежу",
                            "accusative_case": "Воронежем",
                            "instrumental_case": "Воронежем",
                            "prepositional_case": "Воронеже",
                        }
                    ],
                    "active_to": "2024-04-30",
                    "is_active": True,
                },
            ),
            OpenApiExample(
                name="Request Example",
                description="Пример запроса на создание промо акции",
                response_only=True,
                value={
                    "name": "Promo 1",
                    "categories": [1, 2],
                    "products": [1, 2],
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "cities": [1, 2],
                    "active_to": "2024-04-30",
                    "is_active": True,
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновление промо акции",
        summary="Обновление промо акции",
        parameters=[
            OpenApiParameter(
                name="domain",
                description="Домен города",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            )
        ],
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на обновление промо акции",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Promo 1",
                    "categories": [
                        {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 1,
                            "children": 2,
                            "parents": ["Деке", "deke-1"],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description",
                                }
                            ],
                            "category_meta_id": None,
                            "icon": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "image_url": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "is_visible": True,
                            "is_popular": True,
                        },
                    ],
                    "products": [
                        {
                            "title": "Product A",
                            "brand": 1,
                            "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            "slug": "product-a",
                            "city_price": 100.0,
                            "old_price": 120.0,
                            "images": [
                                {
                                    "id": 1,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                                {
                                    "id": 2,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                            ],
                            "category_slug": "category-a",
                        }
                    ],
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "cities": [
                        {
                            "name": "Воронеж",
                            "domain": "example.com",
                            "nominative_case": "Воронеж",
                            "genitive_case": "Воронежа",
                            "dative_case": "Воронежу",
                            "accusative_case": "Воронежем",
                            "instrumental_case": "Воронежем",
                            "prepositional_case": "Воронеже",
                        }
                    ],
                    "active_to": "2024-04-30",
                    "is_active": True,
                },
            ),
            OpenApiExample(
                name="Request Example",
                description="Пример запроса на обновление промо акции",
                response_only=True,
                value={
                    "name": "Promo 1",
                    "categories": [1, 2],
                    "products": [1, 2],
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "cities": [1, 2],
                    "active_to": "2024-04-30",
                    "is_active": True,
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частичное обновление промо акции",
        summary="Частичное обновление промо акции",
        parameters=[
            OpenApiParameter(
                name="domain",
                description="Домен города",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            )
        ],
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на частичное обновление промо акции",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Partial Updated Name for Promo 1",
                    "categories": [
                        {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 1,
                            "children": 2,
                            "parents": ["Деке", "deke-1"],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description",
                                }
                            ],
                            "category_meta_id": None,
                            "icon": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "image_url": "/media/catalog/images/aojw3-ionadi43ujasdkasl.webp",
                            "is_visible": True,
                            "is_popular": True,
                        },
                    ],
                    "products": [
                        {
                            "title": "Product A",
                            "brand": 1,
                            "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            "slug": "product-a",
                            "city_price": 100.0,
                            "old_price": 120.0,
                            "images": [
                                {
                                    "id": 1,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                                {
                                    "id": 2,
                                    "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                                },
                            ],
                            "category_slug": "category-a",
                        }
                    ],
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "cities": [
                        {
                            "name": "Воронеж",
                            "domain": "example.com",
                            "nominative_case": "Воронеж",
                            "genitive_case": "Воронежа",
                            "dative_case": "Воронежу",
                            "accusative_case": "Воронежем",
                            "instrumental_case": "Воронежем",
                            "prepositional_case": "Воронеже",
                        }
                    ],
                    "active_to": "2024-04-30",
                    "is_active": True,
                },
            ),
            OpenApiExample(
                name="Request Example",
                description="Пример запроса на частичное обновление промо акции",
                response_only=True,
                value={
                    "name": "Partial Updated Name for Promo 1"
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удаление промо акции",
        summary="Удаление промо акции",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
