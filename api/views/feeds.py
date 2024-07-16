from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.http import HttpResponse
from django.utils import timezone
from api.serializers.setting import SettingSerializer
from shop.models import Price, Product
from rest_framework.views import APIView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import xml.etree.ElementTree as ET


@method_decorator(cache_page(120 * 60), name='dispatch')  # Кэширование на 2 часа
@extend_schema(tags=["Settings"])
class FeedsView(APIView):

    queryset = Product.objects.all()
    serializer_class = SettingSerializer

    @extend_schema(
        description="Получение xml фидов",
        summary="Получение xml фидов",
        examples=[
            OpenApiExample(
                name="Response Example",
                value="""<yml_catalog date="2024-07-16">
    <shop>
        <name>КровМаркет</name>
        <company>alta-profil</company>
        <url>https://krov.market/</url>
        <offers>
            <offer id="6" available="true">
                <name>Гидро-ветрозащитая диффузионная мембрана ТехноНИКОЛЬ Альфа ВЕНТ 130 ТПУ</name>
                <url>katalog/gidro-vetrozashchitaia-diffuzionnaia-membrana-tekhnonikol-al-fa-vent-130-tpu/gidro-vetrozashchitaia-diffuzionnaia-membrana-tekhnonikol-al-fa-vent-130-tpu-6</url>
                <categoryId>7</categoryId>
                <picture>Ссылка на изображение</picture>
                <vendor>ТЕХНОНИКОЛЬ</vendor>
                <description>Диффузионная мембрана ТЕХНОНИКОЛЬ АЛЬФА ВЕНТ ТПУ 130 – трёхслойный материал с функциональным слоем из паропроницаемого покрытия - термопластичного полиуретана, защищённого с двух сторон полотном из нетканого полипропилена. Воздухонепроницаемая и водонепроницаемая поверхность создает надежную защиту от конвективных потерь тепла и намокания слоя утеплителя. Устойчива к воздействию плесени, бактерий и УФ-излучению.</description>
                <sales_notes>Минимальная партия заказа - 1 шт.</sales_notes>
                <vendorCode>070534</vendorCode>
                <country_of_origin>Россия</country_of_origin>
                <barcode>barcode</barcode>
                <weight>0.5</weight>
                <dimensions>10.0/20.0/30.0</dimensions>
                <cpa>1</cpa>
                <manufacturer_warranty>true</manufacturer_warranty>
                <pickup>true</pickup>
                <store>true</store>
                <outlets>
                    <outlet id="Москва" instock="true" price="1131.00">
                    <city>Москва</city>
                    <address>Адрес магазина</address>
                    <oldprice>1131.00</oldprice>
                    <currencyId>RUB</currencyId>
                    </outlet>
                </outlets>
            </offer>
        </offers>
    </shop>
</yml_catalog>
""",
                response_only=True,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        xml_data = ProductFeed().item_xml(products)
        return HttpResponse(xml_data, content_type="application/xml")


class ProductFeed(Feed):

    def item_extra_kwargs(self, item):
        return {
            "name": item.title,
            "available": item.is_active,
            "description": item.description,
            "sales_notes": "Минимальная партия заказа - 1 шт.",  # Условия продаж
            "categoryId": item.category.id,
            "picture": (
                item.catalog_image.url
                if item.catalog_image and hasattr(item.catalog_imgae, "url")
                else "Ссылка на изображение"
            ),
            "vendor": item.brand.name if item.brand else "Бренд",
            "vendorCode": item.article,  # Код производителя
            "country_of_origin": "Россия",
            "barcode": "barcode",  # Штрихкод
            "weight": 0.5,  # Масса товара
            "manufacturer_warranty": True,  # Гарантия от производителя
            "pickup": True,  # Самовывоз
            "cpa": 1,  # участвует ли предложение в программе "Заказ на Маркете"
            "store": True,  # Возможность покупки товара в розничном магазине
            "dimensions": "10.0/20.0/30.0",  # Габариты (длина ширина высота)
            "delivery": True,
            "price_info": self.item_price_info(item),
        }

    def item_price_info(self, item):
        return [
            {
                "city": (
                    price.city_group.cities.first().name
                    if price.city_group.cities.exists()
                    else "Город"
                ),
                "address": (
                    i.address
                    if (i := price.city_group.cities.first()) and i.address
                    else "Адрес магазина"
                ),
                "price": price.price,
                "old_price": price.old_price,
                "currency": "RUB",
                "instock": item.in_stock,
            }
            for price in Price.objects.filter(product=item)
        ]

    def item_xml(self, products):
        yml_catalog = ET.Element("yml_catalog", date=timezone.now().date().isoformat())
        shop = ET.SubElement(yml_catalog, "shop")

        name = ET.SubElement(shop, "name")
        name.text = settings.SHOP_NAME

        company = ET.SubElement(shop, "company")
        company.text = settings.COMPANY_NAME

        url = ET.SubElement(shop, "url")
        url.text = f"https://{settings.BASE_DOMAIN}/"

        offers = ET.SubElement(shop, "offers")

        for item in products:

            item_extra_kwargs = self.item_extra_kwargs(item)

            offer = ET.SubElement(offers, "offer", id=str(item.id), available="true")

            ET.SubElement(offer, "name").text = item.title
            ET.SubElement(offer, "url").text = item.get_absolute_url()
            ET.SubElement(offer, "categoryId").text = str(item.category.id)
            ET.SubElement(offer, "picture").text = item_extra_kwargs["picture"]
            ET.SubElement(offer, "vendor").text = item_extra_kwargs["vendor"]
            ET.SubElement(offer, "description").text = item.description

            if item_extra_kwargs["sales_notes"]:
                ET.SubElement(offer, "sales_notes").text = item_extra_kwargs[
                    "sales_notes"
                ]
            if item_extra_kwargs["vendorCode"]:
                ET.SubElement(offer, "vendorCode").text = item_extra_kwargs[
                    "vendorCode"
                ]
            if item_extra_kwargs["country_of_origin"]:
                ET.SubElement(offer, "country_of_origin").text = item_extra_kwargs[
                    "country_of_origin"
                ]
            if item_extra_kwargs["barcode"]:
                ET.SubElement(offer, "barcode").text = item_extra_kwargs["barcode"]
            if item_extra_kwargs["weight"]:
                ET.SubElement(offer, "weight").text = str(item_extra_kwargs["weight"])
            if item_extra_kwargs["dimensions"]:
                ET.SubElement(offer, "dimensions").text = item_extra_kwargs[
                    "dimensions"
                ]

            ET.SubElement(offer, "cpa").text = str(item_extra_kwargs["cpa"]).lower()
            ET.SubElement(offer, "manufacturer_warranty").text = str(
                item_extra_kwargs["manufacturer_warranty"]
            ).lower()
            ET.SubElement(offer, "pickup").text = str(
                item_extra_kwargs["pickup"]
            ).lower()
            ET.SubElement(offer, "store").text = str(item_extra_kwargs["store"]).lower()

            outlets = ET.SubElement(offer, "outlets")
            for price in item_extra_kwargs["price_info"]:
                outlet = ET.SubElement(
                    outlets,
                    "outlet",
                    id=str(price["city"]),
                    instock=str(price["instock"]).lower(),
                    price=str(price["price"]),
                )
                ET.SubElement(outlet, "city").text = price["city"]
                ET.SubElement(outlet, "address").text = price["address"]
                if price["old_price"]:
                    ET.SubElement(outlet, "oldprice").text = str(price["old_price"])
                ET.SubElement(outlet, "currencyId").text = price["currency"]

        return ET.tostring(yml_catalog, encoding="utf-8").decode("utf-8")
