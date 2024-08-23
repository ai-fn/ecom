from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
)


from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from api.permissions import ReadOnlyOrAdminPermission
from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.serializers import PageSerializer
from shop.models import Page
from api.views.metadata import OPEN_GRAPH_META_RESPONSE_EXAMPLE


PAGE_REQUEST_EXAMPLE = {
    "title": "Первая страница",
    "h1_tag": "dummy_h1_tag",
    "content": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo " \
                "inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut " \
                "fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, " \
                "consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, " \
                "quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate " \
                "velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?",
    "description": "Описание первой страницы",
    "slug": "pervaya-stranitsa",
    "image": "/media/pages/image1.jpg",
}
PAGE_RESPONSE_EXAMPLE = {
    "id": 1,
    **PAGE_REQUEST_EXAMPLE,
    "opengraph_metadata": OPEN_GRAPH_META_RESPONSE_EXAMPLE,
}
PAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(PAGE_REQUEST_EXAMPLE.items())[:2]}


@extend_schema(
    tags=["Shop"],
    parameters=[
        OpenApiParameter(
            "city_domain",
            type=str,
            required=True,
            description="Домен города"
        )
    ]
)
@extend_schema_view(
    list=extend_schema(
        summary="Получить список страниц",
        description="Возвращает список всех страниц.",
        responses={
            200: OpenApiResponse(
                response=PageSerializer(many=True),
                examples=[OpenApiExample("Пример успешного ответа", value=[])],
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получить страницу",
        description="Возвращает детальную информацию о конкретной странице.",
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
    ),
    create=extend_schema(
        summary="Создать страницу",
        description="Создает новую страницу.",
        request=PageSerializer,
        responses={
            201: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PAGE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    update=extend_schema(
        summary="Обновить страницу",
        description="Обновляет существующую страницу.",
        request=PageSerializer,
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PAGE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]

    ),
    partial_update=extend_schema(
        summary="Частично обновить страницу",
        description="Частично обновляет существующую страницу.",
        request=PageSerializer,
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удалить страницу",
        description="Удаляет существующую страницу.",
        responses={
            204: OpenApiResponse(
                response=None,
                examples=[OpenApiExample("Пример успешного ответа", value=None)],
            )
        },
    ),
    retrieve_by_slug=extend_schema(
        summary="Получение страницы по слагу",
        description="Получение страницы по слагу",
        responses={
            200: OpenApiResponse(
                response=PageSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ]
            )
        }
    ),
)
class PageViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    queryset = Page.objects.order_by("-created_at")
    permission_classes = [ReadOnlyOrAdminPermission]
    serializer_class = PageSerializer


    def get_serializer_context(self):
        data = super().get_serializer_context()
        data["city_domain"] = self.request.query_params.get("city_domain")
        return data


    def get_object(self) -> Page:
        loogup_field: str = self.kwargs.get(self.lookup_field)

        if loogup_field and not loogup_field.isdigit():
            self.lookup_field = self.lookup_url_kwarg = "slug"
            self.kwargs[self.lookup_field] = loogup_field

        return super().get_object()


    @action(detail=False, methods=["get"], url_path="by-slug/(?P<slug>[^/.]+)")
    def retrieve_by_slug(self, request, slug=None, *args, **kwargs):
        """
        Кастомное действие для получения страницы по слагу.
        """
        self.lookup_field = self.lookup_url_kwarg = "slug"
        self.kwargs[self.lookup_field] = slug
        return super().retrieve(request, *args, **kwargs)
