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
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Test",
                        "categories": [
                            {
                                "id": 1,
                                "name": "Деке",
                                "slug": "deke-1",
                                "parent": 1,
                                "category_meta": [
                                    {
                                        "title": "dummy-title",
                                        "description": "dummy-description"
                                    }
                                ],
                                "category_meta_id": 1,
                                "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                                "image_url": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                                "is_visible": True,
                                "is_popular": False,
                            }
                        ],
                        "products": [
                            {
                                "id": 10,
                                "title": "Желоб водосточный 3 м Premium, пломбир",
                                "brand": 1,
                                "image": 1,
                                "slug": "zhelob-vodostochnyi-3-m-premium-plombir-10",
                                "images": [
                                    {
                                        "image_url": "/media/catalog/products/image-cc4937b2-3773-4d1f-970b-8325d2f563ad.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-44d60b64-7c30-45b6-a78c-594f65d02aed.webp"
                                    },
                                ],
                                "icon": "/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                                "image_url": "/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                                "is_visible": True,
                                "in_stock": True,
                                "category_slug": "seriia-premium-3",
                                "search_image": "/media/catalog/products/search-image-44d60b64-7c30-45b6-a78c-594f65d02aed.webp",
                                "catalog_image": "/media/catalog/products/catalog-image-44d60b64-7c30-45b6-a78c-594f65d02aed.webp",
                                "is_popular": False,
                            },
                            {
                                "id": 11,
                                "title": "Желоб водосточный 3 м Premium, шоколад",
                                "brand": 1,
                                "image": 1,
                                "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                "images": [
                                    {
                                        "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                    },
                                ],
                                "in_stock": True,
                                "category_slug": "seriia-premium-3",
                                "search_image": "/media/catalog/products/search-image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp",
                                "catalog_image": "/media/catalog/products/catalog-image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp",
                                "is_popular": False,
                            },
                        ],
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
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
                                "image_url": "http://127.0.0.1:8000catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                        "in_stock": True
                    }
                ],
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удаление промо акции",
        summary="Удаление промо акции",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
