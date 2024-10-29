import os
import xml.etree.ElementTree as ET

from django.utils import timezone
from django.contrib.syndication.views import Feed
from django.conf import settings
from shop.models import Category, Product, Setting, SettingChoices
from shop.utils import get_base_domain


class FeedsService(Feed):

    city_group_name = None

    @classmethod
    def collect_feeds(cls, city_group_name: str, xml_filname: str = "feeds.xml"):
        cls.city_group_name = city_group_name
        products = Product.objects.all()
        categories = Category.objects.values("id", "parent", "name")
        result = cls.item_xml(products, categories)
        feeds_path = os.path.join(settings.FEEDS_PATH, city_group_name)

        xml_path = os.path.join(feeds_path, xml_filname)
        if not os.path.exists(xml_path):
            os.makedirs(feeds_path, exist_ok=False)

        with open(xml_path, "w") as file:
            file.write(result)

        return xml_path

    @classmethod
    def item_extra_kwargs(cls, item):
        data = {
            "delivery": True,
            "name": item.title,
            "available": item.is_active,
            "pickup": True,  # Самовывоз
            "country_of_origin": "Россия",
            "weight": 0.5,  # Масса товара
            "categoryId": item.category.id,
            "description": item.description,
            "barcode": "barcode",  # Штрихкод
            "vendorCode": item.article,  # Код производителя
            "vendor": item.brand.name if item.brand else "Бренд",
            "manufacturer_warranty": True,  # Гарантия от производителя
            "dimensions": "10.0/20.0/30.0",  # Габариты (длина ширина высота)
            "store": True,  # Возможность покупки товара в розничном магазине
            "cpa": 1,  # участвует ли предложение в программе "Заказ на Маркете"
            "sales_notes": "Минимальная партия заказа - 1 шт.",  # Условия продаж
        }
        if item.catalog_image and hasattr(item.catalog_image, "url"):
            data['picture'] = item.catalog_image.url

        if p := item.prices.filter(city_group__name=cls.city_group_name).first():
            data["price"] = float(p.price)
            data["currencyId"] = "RUB"

        return data

    @classmethod
    def item_xml(cls, products, categories):
        yml_catalog = ET.Element(
            "yml_catalog", date=timezone.localtime(timezone.now()).date().isoformat()
        )
        shop = ET.SubElement(yml_catalog, "shop")

        name = ET.SubElement(shop, "name")
        company = ET.SubElement(shop, "company")

        if (shop_name := Setting.objects.filter(predefined_key=SettingChoices.SHOP_NAME)).first():
            name.text = getattr(shop_name, "value_string")

        if (company_name := Setting.objects.filter(predefined_key=SettingChoices.COMPANY_NAME)).first():
            company.text = getattr(company_name, "value_string")

        url = ET.SubElement(shop, "url")
        if base_domain := get_base_domain():
            url.text = f"https://{getattr(base_domain, "value_string")}/"

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

        return ET.tostring(yml_catalog, encoding="utf-8").decode("utf-8")
