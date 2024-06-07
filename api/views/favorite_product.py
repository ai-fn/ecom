from rest_framework import viewsets
from shop.models import FavoriteProduct
from api.serializers import FavoriteProductSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from rest_framework.permissions import IsAuthenticated


@extend_schema_view(
    list=extend_schema(
        summary="Список избранных продуктов",
        description="Возвращает список всех избранных продуктов.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример списка избранных продуктов",
                description="Пример ответа, содержащего список избранных продуктов.",
                value={
                    "id": 1,
                    "user_id": 2,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": 89.00,
                        "old_price": 99.00,
                        "images": [
                            {
                                "image_url": "/media/catalog/products/images/dummy-image.png",
                                "thumb_img": "base64string",
                            }
                        ],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": "/media/catalog/products/images/dummy-image.png",
                        "catalog_image": "/media/catalog/products/images/dummy-image.png",
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "base64string",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            )
        ],
    ),
    create=extend_schema(
        summary="Добавить избранный продукт",
        description="Добавляет новый избранный продукт.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на добавление избранного продукта",
                description="Пример тела запроса для добавления нового избранного продукта.",
                value={"user_id": 2, "product_id": 5118},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при добавлении избранного продукта",
                description="Пример успешного ответа, содержащего добавленный избранный продукт.",
                response_only=True,
                value={
                    "id": 1,
                    "user_id": 2,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": 89.00,
                        "old_price": 99.00,
                        "images": [
                            {
                                "image_url": "/media/catalog/products/images/dummy-image.png",
                                "thumb_img": "base64string",
                            }
                        ],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": "/media/catalog/products/images/dummy-image.png",
                        "catalog_image": "/media/catalog/products/images/dummy-image.png",
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "base64string",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Получить избранный продукт",
        description="Возвращает избранный продукт по ID.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример ответа для одного избранного продукта",
                description="Пример ответа, содержащего данные одного избранного продукта.",
                value={
                    "id": 1,
                    "user_id": 2,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": 89.00,
                        "old_price": 99.00,
                        "images": [
                            {
                                "image_url": "/media/catalog/products/images/dummy-image.png",
                                "thumb_img": "base64string",
                            }
                        ],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": "/media/catalog/products/images/dummy-image.png",
                        "catalog_image": "/media/catalog/products/images/dummy-image.png",
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "base64string",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
            )
        ],
    ),
    update=extend_schema(
        summary="Обновить избранный продукт",
        description="Обновляет информацию об избранном продукте.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на обновление избранного продукта",
                description="Пример тела запроса для обновления существующего избранного продукта.",
                value={"user_id": 2, "product_id": 5118},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при обновлении избранного продукта",
                description="Пример успешного ответа, содержащего обновленный избранный продукт.",
                value={
                    "id": 1,
                    "user_id": 2,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": 89.00,
                        "old_price": 99.00,
                        "images": [
                            {
                                "image_url": "/media/catalog/products/images/dummy-image.png",
                                "thumb_img": "base64string",
                            }
                        ],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": "/media/catalog/products/images/dummy-image.png",
                        "catalog_image": "/media/catalog/products/images/dummy-image.png",
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "base64string",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частично обновить избранный продукт",
        description="Частично обновляет информацию об избранном продукте.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на частичное обновление избранного продукта",
                description="Пример тела запроса для частичного обновления существующего избранного продукта.",
                value={"product_id": 5118},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при частичном обновлении избранного продукта",
                description="Пример успешного ответа, содержащего частично обновленный избранный продукт.",
                value={
                    "id": 1,
                    "user_id": 2,
                    "product": {
                        "id": 5118,
                        "title": "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                        "brand": 5,
                        "article": "068189",
                        "slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke-5118",
                        "city_price": 89.00,
                        "old_price": 99.00,
                        "images": [
                            {
                                "image_url": "/media/catalog/products/images/dummy-image.png",
                                "thumb_img": "base64string",
                            }
                        ],
                        "in_stock": True,
                        "category_slug": "uplotnitel-naia-manzheta-tekhnonikol-al-fa-protekt-l-samokleiashchaiasia-10-shtuk-v-korobke",
                        "brand_slug": "tekhnonikol",
                        "search_image": "/media/catalog/products/images/dummy-image.png",
                        "catalog_image": "/media/catalog/products/images/dummy-image.png",
                        "is_popular": False,
                        "is_new": False,
                        "thumb_img": "base64string",
                        "description": "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                    },
                },
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удалить избранный продукт",
        description="Удаляет избранный продукт.",
    ),
)
@extend_schema(tags=["Shop"])
class FavoriteProductViewSet(viewsets.ModelViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
