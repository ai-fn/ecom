from rest_framework import viewsets
from shop.models import FavoriteProduct
from api.serializers import FavoriteProductSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from rest_framework.permissions import IsAuthenticated


@extend_schema_view(
    tags=["Shop"],
    list=extend_schema(
        summary="Получение списка избранных товаров",
        description="Получение списка избранных товаров для авторизованных пользователей.",
        responses={200: FavoriteProductSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Example Response",
                value=[
                    {
                        "id": 1,
                        "product": {
                            "id": 5118,
                            "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                            "brand": 5,
                            "article": "068189",
                            "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                            "city_price": None,
                            "old_price": None,
                            "images": [],
                            "in_stock": True,
                            "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                            "brand_slug": "tekhnonikol",
                            "search_image": None,
                            "catalog_image": None,
                            "is_popular": False,
                            "is_new": False,
                            "thumb_img": "",
                            "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                        },
                    }
                ],
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Получение конкретного избранного товара.",
        description="Получение конкретного избранного товара по ID.",
        responses={200: FavoriteProductSerializer},
        examples=[
            OpenApiExample(
                "Example Response",
                value={
                    "id": 1,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": None,
                        "old_price": None,
                        "images": [],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": None,
                        "catalog_image": None,
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            )
        ],
    ),
    create=extend_schema(
        summary="Добавление избранного товара",
        description="Добавление избранного товара для авторизованного пользователя.",
        request=FavoriteProductSerializer,
        responses={201: FavoriteProductSerializer},
        examples=[
            OpenApiExample("Example Request", value={"user": 1, "product": 1}),
            OpenApiExample(
                "Example Response",
                value={
                    "id": 1,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": None,
                        "old_price": None,
                        "images": [],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": None,
                        "catalog_image": None,
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            ),
        ],
    ),
    update=extend_schema(
        summary="Изменение существущего избранного товара",
        description="Изменение данных существущего избранного товара.",
        request=FavoriteProductSerializer,
        responses={200: FavoriteProductSerializer},
        examples=[
            OpenApiExample("Example Request", value={"user": 1, "product": 2}),
            OpenApiExample(
                "Example Response",
                value={
                    "id": 1,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": None,
                        "old_price": None,
                        "images": [],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": None,
                        "catalog_image": None,
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частичное изменение существущего избранного товара",
        description="Частичное изменение данных существущего избранного товара.",
        request=FavoriteProductSerializer,
        responses={200: FavoriteProductSerializer},
        examples=[
            OpenApiExample("Example Request", value={"product": 2}),
            OpenApiExample(
                "Example Response",
                value={
                    "id": 1,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": None,
                        "old_price": None,
                        "images": [],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": None,
                        "catalog_image": None,
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удаление избранного товара",
        description="Удаление избранного товара по ID.",
        responses={204: None},
        examples=[OpenApiExample("Example Request", value={})],
    ),
)
@extend_schema(tags=["Shop"])
class FavoriteProductViewSet(viewsets.ModelViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
