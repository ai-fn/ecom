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
                name="Пример запроса",
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
        result = []
        if query:
            headers = {
                "User-Agent": "{}/1.0 ({})".format(settings.ROOT_URLCONF.split(".")[0], settings.EMAIL_HOST_USER)
            }

            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "addressdetails": 1, "limit": 5, "countrycodes": "ru"},
                headers=headers,
            )
            if 200 <= response.status_code < 400:
                suggestions = response.json()
                result = [
                    {"value": suggestion["display_name"]} for suggestion in suggestions
                ]

        return Response(result, status=HTTP_200_OK)
