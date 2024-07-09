from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter

from shop.models import HTMLMetaTags
from api.serializers import HTMLMetaTagSerializer
from api.permissions import ReadOnlyOrAdminPermission


@extend_schema_view(
    list=extend_schema(
        summary="Список метаданных",
        description="Получить список всех метаданных с возможностью фильтрации по типу и идентификатору объекта.",
        responses={
            200: HTMLMetaTagSerializer(many=True),
        },
        examples=[
            OpenApiExample(**{
                "name": "Пример запроса",
                "description": "Пример получения списка метаданных",
                "value": {
                    "results": [
                        {
                            "title": "Купить ноутбук в Москве",
                            "description": "Лучшие ноутбуки в Москве по низким ценам.",
                            "keywords": "ноутбук, купить, Москва",
                            "object_id": 1,
                            "content_type": "product",
                        }
                    ]
                },
                "request_only": True,
            })
        ]
    ),
    retrieve=extend_schema(
        summary="Получить метаданные",
        description="Получить метаданные по ID.",
        responses={
            200: HTMLMetaTagSerializer,
        },
        examples=[
            OpenApiExample(**{
                "name": "Пример запроса",
                "description": "Пример получения метаданных по ID",
                "value": {
                    "title": "Купить ноутбук в Москве",
                    "description": "Лучшие ноутбуки в Москве по низким ценам.",
                    "keywords": "ноутбук, купить, Москва",
                    "object_id": 1,
                    "content_type": "product",
                },
                "request_only": True,
            })
        ]
    ),
    create=extend_schema(
        summary="Создать метаданные",
        description="Создать новые метаданные.",
        request=HTMLMetaTagSerializer,
        responses={
            201: HTMLMetaTagSerializer,
        },
        examples=[
            OpenApiExample(**{
                "name": "Пример запроса",
                "description": "Пример создания метаданных",
                "value": {
                    "title": "Купить ноутбук в Москве",
                    "description": "Лучшие ноутбуки в Москве по низким ценам.",
                    "keywords": "ноутбук, купить, Москва",
                    "object_id": 1,
                    "content_type": "product",
                },
                "request_only": True,
            })
        ]
    ),
    update=extend_schema(
        summary="Обновить метаданные",
        description="Обновить существующие метаданные по ID.",
        request=HTMLMetaTagSerializer,
        responses={
            200: HTMLMetaTagSerializer,
        },
        examples=[
            OpenApiExample(**{
                "name": "Пример запроса",
                "description": "Пример обновления метаданных",
                "value": {
                    "title": "Купить ноутбук в Москве",
                    "description": "Лучшие ноутбуки в Москве по низким ценам.",
                    "keywords": "ноутбук, купить, Москва",
                    "object_id": 1,
                    "content_type": "product",
                },
                "request_only": True,
            })
        ]
    ),
    partial_update=extend_schema(
        summary="Частично обновить метаданные",
        description="Частично обновить существующие метаданные по ID.",
        request=HTMLMetaTagSerializer,
        responses={
            200: HTMLMetaTagSerializer,
        },
        examples=[
            OpenApiExample(**{
                "name": "Пример запроса",
                "description": "Пример частичного обновления метаданных",
                "value": {
                    "title": "Купить ноутбук в Москве",
                    "description": "Лучшие ноутбуки в Москве по низким ценам.",
                    "keywords": "ноутбук, купить, Москва",
                    "object_id": 1,
                    "content_type": "product",
                },
                "request_only": True,
            })
        ]
    ),
    destroy=extend_schema(
        summary="Удалить метаданные",
        description="Удалить метаданные по ID.",
        responses={
            204: None,
        },
        examples=[
            OpenApiExample(**{
                "name": "Пример запроса",
                "description": "Пример удаления метаданных",
                "request_only": True,
            })
        ]
    )
)
@extend_schema(
    tags=['Shop'],
    parameters=[
        OpenApiParameter(
            name="city_domain",
            type=str,
            description="Домен города",
            required=False
    ),]
)
class HTMLMetaTagsViewSet(ModelViewSet):
    queryset = HTMLMetaTags.objects.all()
    serializer_class = HTMLMetaTagSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Получить отформатированный мета тег",
        description="Получить отформатированный мета тег по ID объекта и домену города.",
        parameters=[
            {
                "name": "city_domain",
                "description": "Домен города",
                "required": False,
                "type": "string",
                "example": "moscow"
            }
        ],
        responses={
            200: HTMLMetaTagSerializer,
        },
        examples=[
            {
                "name": "Пример запроса",
                "description": "Пример получения отформатированного мета тега",
                "value": {
                    "title": "Купить ноутбук в Москве",
                    "description": "Лучшие ноутбуки в Москве по низким ценам.",
                    "keywords": "ноутбук, купить, Москва",
                    "object_id": 1,
                    "content_type": "product",
                }
            }
        ]
    )
    def formatted_meta(self, request, pk=None):
        obj = self.get_object()
        city_domain = request.query_params.get('city_domain')
        title = obj.get_formatted_meta_tag("title", city_domain)
        description = obj.get_formatted_meta_tag("description", city_domain)
        return Response({
            "title": title,
            "description": description,
            "keywords": obj.keywords,
            "object_id": obj.object_id,
            "content_type": obj.content_type.id,
        })