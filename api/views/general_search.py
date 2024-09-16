from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from api.mixins import GeneralSearchMixin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from elasticsearch import ConnectionError


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
            name="city_domain",
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

        try:
            result, _ = self.g_search(query, domain)
            categorized_results = {index: result[index]["serialized"] for index in result}
        except ConnectionError as e:
            logger.error(str(e))
            return Response({"error": f"Error connecting to elasticsearch: {str(e)}"}, status=HTTP_503_SERVICE_UNAVAILABLE)

        return Response(categorized_results, status=HTTP_200_OK)
