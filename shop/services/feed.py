import os
import xml.etree.ElementTree as ET

from django.utils import timezone
from django.contrib.syndication.views import Feed
from django.conf import settings
from shop.models import Category, Price, Product


class FeedsService(Feed):

    @classmethod
    def collect_feeds(cls, xml_filname: str = "feeds.xml"):
        products = Product.objects.all()
        categories = Category.objects.values("id", "parent", "name")
        result = cls.item_xml(products, categories)
        feeds_path = settings.FEEDS_PATH

        xml_path = os.path.join(feeds_path, xml_filname)
        if not os.path.exists(xml_path):
            os.makedirs(feeds_path, exist_ok=True)

        with open(xml_path, "w") as file:
            file.write(result)

        return xml_path

    @classmethod
    def item_extra_kwargs(cls, item):
        return {
            "name": item.title,
            "available": item.is_active,
            "description": item.description,
            "sales_notes": "Минимальная партия заказа - 1 шт.",  # Условия продаж
            "categoryId": item.category.id,
            "picture": (
                item.catalog_image.url
                if item.catalog_image and hasattr(item.catalog_image, "url")
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
            "price_info": cls.item_price_info(item),
        }

    @classmethod
    def item_price_info(cls, item):
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
                "price": float(price.price),
                "old_price": price.old_price,
                "currency": "RUB",
                "instock": item.in_stock,
            }
            for price in Price.objects.filter(product=item)
        ]

    @classmethod
    def item_xml(cls, products, categories):
        yml_catalog = ET.Element(
            "yml_catalog", date=timezone.localtime(timezone.now()).date().isoformat()
        )
        shop = ET.SubElement(yml_catalog, "shop")

        name = ET.SubElement(shop, "name")
        name.text = settings.SHOP_NAME

        company = ET.SubElement(shop, "company")
        company.text = settings.COMPANY_NAME

        url = ET.SubElement(shop, "url")
        url.text = f"https://{settings.BASE_DOMAIN}/"

        offers = ET.SubElement(shop, "offers")
        categories_elements = ET.SubElement(shop, "categories")

        for category in categories:
            ctg_kwargs = {"id": str(category["id"])}
            if parent := category.get("parent"):
                ctg_kwargs["parentId"] = str(parent)

            category = ET.SubElement(
                categories_elements, "category", **ctg_kwargs
            ).text = category["name"]

        for item in products:

            item_extra_kwargs = cls.item_extra_kwargs(item)

            offer = ET.SubElement(offers, "offer", id=str(item.id), available="true")

            ET.SubElement(offer, "name").text = item.title
            ET.SubElement(offer, "url").text = item.get_absolute_url()
            ET.SubElement(offer, "categoryId").text = str(item.category.id)
            ET.SubElement(offer, "picture").text = item_extra_kwargs["picture"]
            ET.SubElement(offer, "vendor").text = item_extra_kwargs["vendor"]
            ET.SubElement(offer, "description").text = item.description

            if sales_notes := item_extra_kwargs.get("sales_notes"):
                ET.SubElement(offer, "sales_notes").text = sales_notes

            if vendorCode := item_extra_kwargs.get("vendorCode"):
                ET.SubElement(offer, "vendorCode").text = vendorCode

            if country_of_origin := item_extra_kwargs.get("country_of_origin"):
                ET.SubElement(offer, "country_of_origin").text = country_of_origin

            if barcode := item_extra_kwargs.get("barcode"):
                ET.SubElement(offer, "barcode").text = barcode

            if weight := item_extra_kwargs.get("weight"):
                ET.SubElement(offer, "weight").text = str(weight)

            if dimensions := item_extra_kwargs.get("dimensions"):
                ET.SubElement(offer, "dimensions").text = dimensions

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
