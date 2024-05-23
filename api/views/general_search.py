from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

from api.mixins import GeneralSearchMixin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["Search"],
    summary="Поиск товаров в каталоге",
    description="Поиск товаров в катологе",
    parameters=[
        OpenApiParameter(
            name="q",
            description="Search query to filter results by name, description, reviews, etc.",
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="domain",
            description="Domain to filter prices by city or region",
            required=False,
            type=OpenApiTypes.STR,
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)
class GeneralSearchView(GeneralSearchMixin, APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        domain = self.request.query_params.get("city_domain", "")
        query = self.request.query_params.get("q", "")

        categorized_results = self.g_search(query, domain)
        return Response(categorized_results)
