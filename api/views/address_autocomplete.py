from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


class AddressAutocompleate(APIView):
    permission_classes = [AllowAny]
    serializer_class = None

    @extend_schema(
        tags=["api"],
        summary="Подсказки для адреса",
        description="Получение подсказок для автозаполнения адреса",
        parameters=[OpenApiParameter(name="q", type=str, default="москва патрики")],
        examples=[
            OpenApiExample(
                name="Request Example",
                value={
                    "result": [
                        {
                            "value": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия"
                        }
                    ]
                },
                response_only=True,
            )
        ],
    )
    def get(self, request):
        query = request.GET.get("q", "")
        if query:
            headers = {
                "User-Agent": request.META.get('HTTP_USER_AGENT', 'Mozilla/5.0')
            }

            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "addressdetails": 1, "limit": 5, "countrycodes": "ru"},
                headers=headers,
            )
            if response.status_code >= 200 and 400 > response.status_code:
                suggestions = response.json()
                result = [
                    {"value": suggestion["display_name"]} for suggestion in suggestions
                ]
                return Response(result, status=HTTP_200_OK)
        return Response([], status=HTTP_200_OK)
