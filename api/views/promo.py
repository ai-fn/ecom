from django.http import Http404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from account.models import City
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
    responses={200: PromoSerializer(many=True)},
    description="Retrieves promotions filtered by the domain of the city.",
)
class PromoViewSet(ModelViewSet):

    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_permissions(self):
        if self.action == "active_promos":
            return [AllowAny()]

        return super().get_permissions()

    def get_queryset(self):
        # Получаем домен из параметров запроса
        domain = self.request.query_params.get("domain")
        if not domain:
            raise Http404("Domain parameter is required to filter promotions.")

        # Находим города, соответствующие этому домену
        cities = City.objects.filter(domain=domain)
        if not cities.exists():
            raise Http404("No city found with the given domain.")

        # Возвращаем промоакции, связанные с найденными городами
        return self.queryset.filter(cities__in=cities).distinct()
    
    @extend_schema(
        description="Получение информации обо всех активных акциях",
        summary="Получение информации обо всех активных акциях",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Promo Name",
                        "category": {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 2,
                            "children": 2,
                            "parents": [
                                "Деке",
                                "deke-1"
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description"
                                }
                            ],
                            "category_meta_id": 1,
                            "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "is_visible": True,
                            "is_popular": False,
                        },
                        "product": {
                            "id": 3733,
                            "category": {
                                "id": 1,
                                "name": "Category A",
                                "slug": "category-a",
                                "order": 1,
                                "parent": 2,
                                "children": 2,
                                "parents": [
                                    "Деке",
                                    "deke-1"
                                ],
                                "category_meta": [
                                    {
                                        "title": "dummy-title",
                                        "description": "dummy-description"
                                    }
                                ],
                                "category_meta_id": 1,
                                "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                                "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                                "is_visible": True,
                                "is_popular": False,
                            },
                            "title": "Желоб водосточный 3 м Premium, шоколад",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "description": "Желоб водосточный 3 м Premium, пломбир",
                            "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                            "created_at": "2024-03-11T13:45:20.574851+03:00",
                            "characteristic_values": [
                                {
                                    "id": 89977,
                                    "characteristic_name": "Выбранный цвет",
                                    "value": "Шоколад (RAL 8019)",
                                },
                                {
                                    "id": 89978,
                                    "characteristic_name": "Вес брутто",
                                    "value": "18.3 кг",
                                },
                            ],
                            "images": [
                                {
                                    "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                                },
                                {
                                    "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                                },
                            ],
                            "in_stock": True
                        },
                        "image": "",
                        "cities": [
                            {
                                "name": "Москва",
                                "domain": "msk.krov.market",
                                "nominative_case": "Москва",
                                "genitive_case": "Москвы",
                                "dative_case": "Москве",
                                "accusative_case": "Москвой",
                                "instrumental_case": "Москвой",
                                "prepositional_case": "Москве",
                            }
                        ],
                        "active_to": "2024-12-13",
                        "is_active": True,
                    }
                ]
            )
        ]
    )
    @action(detail=False, methods=["get"])
    def active_promos(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().filter(is_active=True)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение списка промо акций",
        summary="Получение списка промо акций",
        operation_id="api_promos_list",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Promo Name",
                        "category": {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 2,
                            "children": 2,
                            "parents": [
                                "Деке",
                                "deke-1"
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description"
                                }
                            ],
                            "category_meta_id": 1,
                            "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "is_visible": True,
                            "is_popular": False,
                        },
                        "product": {
                            "id": 3733,
                            "category": {
                                "id": 132,
                                "name": "Серия Premium",
                                "slug": "seriya-premium",
                                "order": 15,
                                "parent": 128,
                                "children": [
                                    ["Водосточные системы", "vodostochnyie-sistemyi"]
                                ],
                                "parents": [
                                    ["Деке", "deke"],
                                ],
                                "category_meta": [
                                    {
                                        "title": "dummy title",
                                        "description": "dummy description ",
                                    },
                                ],
                                "icon": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                                "image_url": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                                "is_visible": True,
                            },
                            "title": "Желоб водосточный 3 м Premium, шоколад",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "description": "Желоб водосточный 3 м Premium, пломбир",
                            "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                            "created_at": "2024-03-11T13:45:20.574851+03:00",
                            "characteristic_values": [
                                {
                                    "id": 89977,
                                    "characteristic_name": "Выбранный цвет",
                                    "value": "Шоколад (RAL 8019)",
                                },
                                {
                                    "id": 89978,
                                    "characteristic_name": "Вес брутто",
                                    "value": "18.3 кг",
                                },
                            ],
                            "images": [
                                {
                                    "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                                },
                                {
                                    "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                                },
                            ],
                            "in_stock": True
                        },
                        "image": "",
                        "cities": [
                            {
                                "name": "Москва",
                                "domain": "msk.krov.market",
                                "nominative_case": "Москва",
                                "genitive_case": "Москвы",
                                "dative_case": "Москве",
                                "accusative_case": "Москвой",
                                "instrumental_case": "Москвой",
                                "prepositional_case": "Москве",
                            }
                        ],
                        "active_to": "2024-12-13",
                        "is_active": False,
                    }
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Получение информации о конкретной промо акции",
        summary="Получение информации о конкретной промо акции",
        operation_id="api_promos_retrieve",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Promo Name",
                    "category": {
                        "id": 1,
                        "name": "Category A",
                        "slug": "category-a",
                        "order": 1,
                        "parent": 2,
                        "children": 2,
                        "parents": [
                            "Деке",
                            "deke-1"
                        ],
                        "category_meta": [
                            {
                                "title": "dummy-title",
                                "description": "dummy-description"
                            }
                        ],
                        "category_meta_id": 1,
                        "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "is_visible": True,
                        "is_popular": False,
                    },
                    "product": {
                        "id": 3733,
                        "category": {
                                "id": 1,
                                "name": "Category A",
                                "slug": "category-a",
                                "order": 1,
                                "parent": 2,
                                "children": 2,
                                "parents": [
                                    "Деке",
                                    "deke-1"
                                ],
                                "category_meta": [
                                    {
                                        "title": "dummy-title",
                                        "description": "dummy-description"
                                    }
                                ],
                                "category_meta_id": 1,
                                "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                                "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                                "is_visible": True,
                                "is_popular": False,
                        },
                        "title": "Желоб водосточный 3 м Premium, шоколад",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                        "created_at": "2024-03-11T13:45:20.574851+03:00",
                        "characteristic_values": [
                            {
                                "id": 89977,
                                "characteristic_name": "Выбранный цвет",
                                "value": "Шоколад (RAL 8019)",
                            },
                            {
                                "id": 89978,
                                "characteristic_name": "Вес брутто",
                                "value": "18.3 кг",
                            },
                        ],
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                        "in_stock": True
                    },
                    "image": "",
                    "cities": [
                        {
                            "name": "Москва",
                            "domain": "msk.krov.market",
                            "nominative_case": "Москва",
                            "genitive_case": "Москвы",
                            "dative_case": "Москве",
                            "accusative_case": "Москвой",
                            "instrumental_case": "Москвой",
                            "prepositional_case": "Москве",
                        }
                    ],
                    "active_to": "2024-12-13",
                    "is_active": True,
                }
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Создание промо акции",
        summary="Создание промо акции",
        examples=[
            OpenApiExample(
                name="Creation Example",
                value={
                    "name": "Promo Name",
                    "category_id": 13,
                    "product_id": 6,
                    "image": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp",
                    "cities_id": [
                        1, 2, 3
                    ],
                    "active_to": "2024-12-13",
                }
            ),
            OpenApiExample(
                name="Creation Response Example",
                value={
                    "id": 1,
                    "name": "Promo Name",
                    "category": {
                        "id": 1,
                        "name": "Category A",
                        "slug": "category-a",
                        "order": 1,
                        "parent": 2,
                        "children": 2,
                        "parents": [
                            "Деке",
                            "deke-1"
                        ],
                        "category_meta": [
                            {
                                "title": "dummy-title",
                                "description": "dummy-description"
                            }
                        ],
                        "category_meta_id": 1,
                        "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "is_visible": True
                    },
                    "product": {
                        "id": 3733,
                        "category": {
                            "id": 132,
                            "name": "Серия Premium",
                            "slug": "seriya-premium",
                            "order": 15,
                            "parent": 128,
                            "children": [
                                ["Водосточные системы", "vodostochnyie-sistemyi"]
                            ],
                            "parents": [
                                ["Деке", "deke"],
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy title",
                                    "description": "dummy description ",
                                },
                            ],
                            "icon": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "image_url": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "is_visible": True,
                            "is_popular": False,
                        },
                        "title": "Желоб водосточный 3 м Premium, шоколад",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                        "created_at": "2024-03-11T13:45:20.574851+03:00",
                        "characteristic_values": [
                            {
                                "id": 89977,
                                "characteristic_name": "Выбранный цвет",
                                "value": "Шоколад (RAL 8019)",
                            },
                            {
                                "id": 89978,
                                "characteristic_name": "Вес брутто",
                                "value": "18.3 кг",
                            },
                        ],
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                        "in_stock": True
                    },
                    "image": "",
                    "cities": [
                        {
                            "name": "Москва",
                            "domain": "msk.krov.market",
                            "nominative_case": "Москва",
                            "genitive_case": "Москвы",
                            "dative_case": "Москве",
                            "accusative_case": "Москвой",
                            "instrumental_case": "Москвой",
                            "prepositional_case": "Москве",
                        }
                    ],
                    "active_to": "2024-12-13",
                    "is_active": True,
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Изменение промо акции",
        summary="Изменение промо акции",
        examples=[
            OpenApiExample(
                name="Creation Example",
                value={
                    "name": "Promo Name",
                    "category_id": 2,
                    "product_id": 13,
                    "image": "",
                    "cities_id": [
                        1
                    ],
                    "active_to": "2024-12-13",
                    "is_active": True,
                }
            ),
            OpenApiExample(
                name="Updation Response Example",
                value={
                    "id": 1,
                    "name": "Promo Name",
                    "category": {
                        "id": 2,
                        "name": "Category A",
                        "slug": "category-a",
                        "order": 1,
                        "parent": 2,
                        "children": 2,
                        "parents": [
                            "Деке",
                            "deke-1"
                        ],
                        "category_meta": [
                            {
                                "title": "dummy-title",
                                "description": "dummy-description"
                            }
                        ],
                        "category_meta_id": 1,
                        "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "is_visible": True
                    },
                    "product": {
                        "id": 13,
                        "category": {
                            "id": 132,
                            "name": "Серия Premium",
                            "slug": "seriya-premium",
                            "order": 15,
                            "parent": 128,
                            "children": [
                                ["Водосточные системы", "vodostochnyie-sistemyi"]
                            ],
                            "parents": [
                                ["Деке", "deke"],
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy title",
                                    "description": "dummy description ",
                                },
                            ],
                            "icon": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "image_url": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "is_visible": True,
                            "is_popular": False,
                        },
                        "title": "Желоб водосточный 3 м Premium, шоколад",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                        "created_at": "2024-03-11T13:45:20.574851+03:00",
                        "characteristic_values": [
                            {
                                "id": 89977,
                                "characteristic_name": "Выбранный цвет",
                                "value": "Шоколад (RAL 8019)",
                            },
                            {
                                "id": 89978,
                                "characteristic_name": "Вес брутто",
                                "value": "18.3 кг",
                            },
                        ],
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                        "in_stock": True
                    },
                    "image": "",
                    "cities": [
                        {
                            "name": "Москва",
                            "domain": "msk.krov.market",
                            "nominative_case": "Москва",
                            "genitive_case": "Москвы",
                            "dative_case": "Москве",
                            "accusative_case": "Москвой",
                            "instrumental_case": "Москвой",
                            "prepositional_case": "Москве",
                        }
                    ],
                    "active_to": "2024-12-13",
                    "is_active": True,
                }
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Частичное изменение промо акции",
        summary="Частичное изменение промо акции",
        examples=[
            OpenApiExample(
                name="Creation Example",
                request_only=True,
                value={
                    "name": "UPdated Promo Name",
                    "active_to": "2024-10-11",
                }
            ),
            OpenApiExample(
                name="Creation Example",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Updated Promo Name",
                    "category": {
                        "id": 1,
                        "name": "Category A",
                        "slug": "category-a",
                        "order": 1,
                        "parent": 2,
                        "children": 2,
                        "parents": [
                            "Деке",
                            "deke-1"
                        ],
                        "category_meta": [
                            {
                                "title": "dummy-title",
                                "description": "dummy-description"
                            }
                        ],
                        "category_meta_id": 1,
                        "icon": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "image_url": "catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                        "is_visible": True
                    },
                    "product": {
                        "id": 3733,
                        "category": {
                            "id": 132,
                            "name": "Серия Premium",
                            "slug": "seriya-premium",
                            "order": 15,
                            "parent": 128,
                            "children": [
                                ["Водосточные системы", "vodostochnyie-sistemyi"]
                            ],
                            "parents": [
                                ["Деке", "deke"],
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy title",
                                    "description": "dummy description ",
                                },
                            ],
                            "icon": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "image_url": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "is_visible": True,
                        },
                        "title": "Желоб водосточный 3 м Premium, шоколад",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                        "created_at": "2024-03-11T13:45:20.574851+03:00",
                        "characteristic_values": [
                            {
                                "id": 89977,
                                "characteristic_name": "Выбранный цвет",
                                "value": "Шоколад (RAL 8019)",
                            },
                            {
                                "id": 89978,
                                "characteristic_name": "Вес брутто",
                                "value": "18.3 кг",
                            },
                        ],
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                        "in_stock": True
                    },
                    "image": "",
                    "cities": [
                        {
                            "name": "Москва",
                            "domain": "msk.krov.market",
                            "nominative_case": "Москва",
                            "genitive_case": "Москвы",
                            "dative_case": "Москве",
                            "accusative_case": "Москвой",
                            "instrumental_case": "Москвой",
                            "prepositional_case": "Москве",
                        }
                    ],
                    "active_to": "2024-10-11",
                    "is_active": True,
                }
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Удаление промо акции",
        summary="Удаление промо акции",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
