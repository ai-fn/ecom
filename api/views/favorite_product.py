from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets

from shop.models import FavoriteProduct
from api.serializers import FavoriteProductSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, OpenApiResponse
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
                                "id": 1,
                                "name": "updated_example",
                                "thumb_img": "thumb_example_updated.png",
                                "image": "/media/catalog/products/images/example_updated.png",
                                "is_active": True,
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
                        "is_acitve": True,
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
                "Пример запроса (с указанием user_id)",
                summary="Пример запроса на добавление избранного продукта (с указанием user_id)",
                description="Пример тела запроса для добавления нового избранного продукта.",
                value={
                    "user_id": 2,
                    "product_id": 5118,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример запроса (без указания user_id)",
                summary="Пример запроса на добавление избранного продукта (без указания user_id)",
                description="Пример тела запроса для добавления нового избранного продукта.",
                value={
                    "product_id": 5118,
                },
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
                                "id": 1,
                                "name": "updated_example",
                                "thumb_img": "thumb_example_updated.png",
                                "image": "/media/catalog/products/images/example_updated.png",
                                "is_active": True,
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
                        "is_acitve": True,
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
                                "id": 1,
                                "name": "updated_example",
                                "thumb_img": "thumb_example_updated.png",
                                "image": "/media/catalog/products/images/example_updated.png",
                                "is_active": True,
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
                        "is_acitve": True,
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
                                "id": 1,
                                "name": "updated_example",
                                "thumb_img": "thumb_example_updated.png",
                                "image": "/media/catalog/products/images/example_updated.png",
                                "is_active": True,
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
                        "is_acitve": True,
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
                                "id": 1,
                                "name": "updated_example",
                                "thumb_img": "thumb_example_updated.png",
                                "image": "/media/catalog/products/images/example_updated.png",
                                "is_active": True,
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
                        "is_acitve": True,
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

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.data.get("user_id"):
            request.data["user_id"] = self.request.user.pk

        return super().create(request, *args, **kwargs)

    @extend_schema(
        operation_id='delete_favorite_by_product_id',
        summary='Удаление продукта из избранного по ID продукта',
        description='Удаление продукта из избранного по ID продукта.',
        parameters=[
            OpenApiParameter(
                name='product_id',
                location=OpenApiParameter.PATH,
                description='ID продукта для удаления из избранного',
                required=True,
                type=int
            )
        ],
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description='Продукт успешно удален из избранного'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Продукт не найден в избранном')
        },
        methods=['DELETE'],
    )
    @action(detail=False, methods=['delete'], url_path='delete-by-product-id/(?P<product_id>\d+)')
    def delete_by_prod(self, request, product_id=None, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            queryset.get(product__id=product_id).delete()
        except FavoriteProduct.DoesNotExist:
            return Response({"detail": f"Favorite product with product_id '{product_id}' not found."}, status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)
