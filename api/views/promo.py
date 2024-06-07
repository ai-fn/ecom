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
    parameters=[
        OpenApiParameter(
            name="domain",
            description="Домен города",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        )
    ],
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
        self.domain = self.request.query_params.get("domain")
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
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "Test",
                            "categories": [],
                            "products": [],
                            "image": "/media/promo/image-70e50210-8678-4b3a-90f9-3626526c11cb.webp",
                            "cities": [
                                {
                                    "id": 46,
                                    "name": "Воронеж",
                                    "domain": "voronezh",
                                    "nominative_case": "Воронеж",
                                    "genitive_case": "Воронежа",
                                    "dative_case": "Воронежу",
                                    "accusative_case": "Воронеж",
                                    "instrumental_case": "Воронежем",
                                    "prepositional_case": "Воронеже",
                                },
                                {
                                    "id": 45,
                                    "name": "Москва",
                                    "domain": "moskva",
                                    "nominative_case": "Москва",
                                    "genitive_case": "Москвы",
                                    "dative_case": "Москве",
                                    "accusative_case": "Москву",
                                    "instrumental_case": "Москвой",
                                    "prepositional_case": "Москве",
                                },
                            ],
                            "active_to": "2024-04-05",
                            "is_active": True,
                            "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                        }
                    ],
                },
            ),
        ],
    )
    @action(methods=["get"], detail=False)
    def active_promos(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(is_active=True)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение списка промо акций",
        summary="Получение списка промо акций",
        operation_id="api_promos_list",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение списка всех промо акций",
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
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение промо акции по уникальному идентификатору",
        summary="Получение промо акции по уникальному идентификатору",
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
                value={"name": "Partial Updated Name for Promo 1"},
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
