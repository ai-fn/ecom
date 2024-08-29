from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import ItemSetElementSerializer, ItemSetSerializer
from api.mixins import CacheResponse, ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE
from api.views.banner import BANNER_IMAGE_RESPONSE_EXAMPLE
from api.views.category import CATEGORY_RESPONSE_EXAMPLE
from api.views.promo import PROMO_RESPONSE_EXAMPLE
from shop.models import ItemSet, ItemSetElement


# cutom pagination for item set viewset
class ItemSetPaginate(PageNumberPagination):
    page_size = 1


ITEM_SET_ELEMENT_RESPONSE_EXAMPLE = {
    "id": 1,
    "order": 1,
    "item_set": 1,
    "content_object": UNAUTHORIZED_RESPONSE_EXAMPLE,
}
ITEM_SET_BANNER_ELEMENT_RESPONSE_EXAMPLE = {
    **ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
    "content_object": BANNER_IMAGE_RESPONSE_EXAMPLE,
}
ITEM_SET_CATEGORY_ELEMENT_RESPONSE_EXAMPLE = {
    **ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
    "content_object": CATEGORY_RESPONSE_EXAMPLE,
}
ITEM_SET_PROMO_ELEMENT_RESPONSE_EXAMPLE = {
    **ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
    "content_object": PROMO_RESPONSE_EXAMPLE,
}
ITEM_SET_ELEMENT_REQUEST_EXAMPLE = {
    "item_set": 1,
    "order": 1,
    "content_type": 1,
    "object_id": 1,
}
ITEM_SET_ELEMENT_PARTIAL_UPDATE_EXAMPLE = {
    "item_set": 1,
}

ITEM_SET_RESPONSE_EXAMPLE = {
    "id": 1,
    "title": "dummy-title",
    "description": "dummy-description",
    "itemset_type": "product",
    "grid_type": None,
    "order": 1,
    "elements": [ITEM_SET_ELEMENT_RESPONSE_EXAMPLE],
}
ITEM_SET_BANNER_RESPONSE_EXAMPLE = {
    **ITEM_SET_RESPONSE_EXAMPLE,
    "itemset_type": "banner",
    "grid_type": "grid-1",
    "elements": [ITEM_SET_BANNER_ELEMENT_RESPONSE_EXAMPLE]
}
ITEM_SET_REQUEST_EXAMPLE = {
    "title": "dummy-title",
    "description": "dummy-description",
    "itemset_type": "product",
    "grid_type": "grid-1",
    "order": 1,
    "elements": [1, 2, 3],
}
ITEM_SET_PARTIAL_UPDATE_EXAMPLE = {
    "title": "dummy-title",
}


@extend_schema_view(
    list=extend_schema(
        summary="Получение наборов объектов",
        description="Получение наборов объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_RESPONSE_EXAMPLE,
                    ),
                    OpenApiExample(
                        "Пример ответа для набора банеров",
                        value=ITEM_SET_BANNER_RESPONSE_EXAMPLE,
                    ),
                    OpenApiExample(
                        "Пример ответа для набора акций",
                        value=ITEM_SET_PROMO_ELEMENT_RESPONSE_EXAMPLE,
                    ),
                    OpenApiExample(
                        "Пример ответа для набора категорий",
                        value=ITEM_SET_CATEGORY_ELEMENT_RESPONSE_EXAMPLE,
                    ),
                ]
            )
        }
    ),
    retrieve=extend_schema(
        summary="Получение набора объектов",
        description="Получение набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_RESPONSE_EXAMPLE,
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        summary="Создание набора объектов",
        description="Создание набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=ITEM_SET_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    update=extend_schema(
        summary="Обновление набора объектов",
        description="Обновление набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=ITEM_SET_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Частичное обновление набора объектов",
        description="Частичное обновление набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=ITEM_SET_PARTIAL_UPDATE_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удаление набора объектов",
        description="Удаление набора объектов",
        responses={
            204: None,
        }
    ),
)
@extend_schema(
    tags=["Shop"],
    parameters=[
        OpenApiParameter(
            "city_domain",
            type=str,
            required=False,
            description="City domain"
        )
    ]
)
class ItemSetViewSet(ModelViewSet):
    queryset = ItemSet.objects.all()
    serializer_class = ItemSetSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not request.user.is_staff:
            self.pagination_class = ItemSetPaginate
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if cd := self.request.query_params.get("city_domain"):
            context["city_domain"] = cd

        return context


@extend_schema_view(
    list=extend_schema(
        summary="Получение элементов наборов объектов",
        description="Получение элементов наборов объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
                    )
                ]
            )
        }
    ),
    retrieve=extend_schema(
        summary="Получение элемента набора объектов",
        description="Получение элемента набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        summary="Создание элемента набора объектов",
        description="Создание элемента набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=ITEM_SET_ELEMENT_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    update=extend_schema(
        summary="Обновление элемента набора объектов",
        description="Обновление элемента набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=ITEM_SET_ELEMENT_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Частичное обновление элемента набора объектов",
        description="Частичное обновление элемента набора объектов",
        responses={
            200: OpenApiResponse(
                response=ItemSetSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=ITEM_SET_ELEMENT_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=ITEM_SET_ELEMENT_PARTIAL_UPDATE_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удаление элемента набора объектов",
        description="Удаление элемента набора объектов",
        responses={
            204: None,
        }
    ),
)
@extend_schema(
    tags=["Shop"]
)
class ItemSetElementViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet):
    queryset = ItemSetElement.objects.all()
    serializer_class = ItemSetElementSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
