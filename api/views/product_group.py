from rest_framework import viewsets
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
)
from shop.models import ProductGroup
from api.serializers import ProductGroupSerializer


PRODUCT_FOR_NON_IMAGE_GROUP_EXAMPLE = {
    "id": 1,
    "title": "dummy-title",
    "slug": "dummy-slug",
    "category_slug": "dummy-category_slug",
    "characteristics": [
        {
            "id": 1,
            "value": "100",
            "characteristic__name": "Длина",
        }
    ],
    "is_selected": True,
}
PRODUCT_FOR_IMAGE_GROUP_EXAMPLE = {
    **PRODUCT_FOR_NON_IMAGE_GROUP_EXAMPLE,
    "catalog_image": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp"
}

PRODUCT_GROUP_REQUEST_EXAMPLE = {
    "name": "Группа 1",
    "products": [1],
    "characteristic": "Цвет",
}
PRODUCT_GROUP_RESPONSE_EXAMPLE = {
    "id": 1,
    **PRODUCT_GROUP_REQUEST_EXAMPLE,
    "products": [
        PRODUCT_FOR_NON_IMAGE_GROUP_EXAMPLE, PRODUCT_FOR_IMAGE_GROUP_EXAMPLE
    ]
}
PRODUCT_GROUP_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(PRODUCT_GROUP_REQUEST_EXAMPLE.items())[:2]
}


@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех групп продуктов",
        description="Возвращает список всех групп продуктов.",
        responses={
            200: OpenApiResponse(
                response=ProductGroupSerializer(many=True),
                description="Список групп продуктов успешно получен.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Список групп продуктов",
                        value=PRODUCT_GROUP_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получить информацию о группе продуктов",
        description="Возвращает подробную информацию о группе продуктов по ID.",
        responses={
            200: OpenApiResponse(
                response=ProductGroupSerializer,
                description="Информация о группе продуктов успешно получена.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Информация о группе продуктов",
                        value=PRODUCT_GROUP_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
    ),
    create=extend_schema(
        summary="Создать новую группу продуктов",
        description="Создает новую группу продуктов.",
        request=ProductGroupSerializer,
        responses={
            201: OpenApiResponse(
                response=ProductGroupSerializer,
                description="Группа продуктов успешно создана.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Группа продуктов создана",
                        value=PRODUCT_GROUP_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на создание группы продуктов",
                request_only=True,
                value=PRODUCT_GROUP_REQUEST_EXAMPLE,
            )
        ],
    ),
    update=extend_schema(
        summary="Обновить группу продуктов",
        description="Обновляет информацию о группе продуктов.",
        request=ProductGroupSerializer,
        responses={
            200: OpenApiResponse(
                response=ProductGroupSerializer,
                description="Группа продуктов успешно обновлена.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Группа продуктов обновлена",
                        value=PRODUCT_GROUP_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на обновление группы продуктов",
                request_only=True,
                value=PRODUCT_GROUP_REQUEST_EXAMPLE,
            )
        ],
    ),
    partial_update=extend_schema(
        summary="Частично обновить группу продуктов",
        description="Частично обновляет определенные поля группы продуктов.",
        request=ProductGroupSerializer,
        responses={
            200: OpenApiResponse(
                response=ProductGroupSerializer,
                description="Группа продуктов частично обновлена.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Частичное обновление группы продуктов",
                        value=PRODUCT_GROUP_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на частичное обновление группы продуктов",
                request_only=True,
                value=PRODUCT_GROUP_PARTIAL_UPDATE_REQUEST_EXAMPLE,
            )
        ],
    ),
    destroy=extend_schema(
        summary="Удалить группу продуктов",
        description="Удаляет группу продуктов по ID.",
        responses={
            204: OpenApiResponse(description="Группа продуктов успешно удалена.")
        },
    ),
)
class ProductGroupViewSet(viewsets.ModelViewSet):
    queryset = ProductGroup.objects.order_by("-created_at")
    serializer_class = ProductGroupSerializer
