import os
import xml.etree.ElementTree as ET

from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.syndication.views import Feed
from django.core.files.storage import default_storage

from account.models import City, CityGroup
from shop.utils import get_base_domain, get_shop_name
from shop.models import Category, Product, Setting, SettingChoices


class FeedsService(Feed):

    schema = "https"
    city_group_name = None

    @classmethod
    def collect_feeds(cls, city_group_name: str):
        cls.city_group_name = city_group_name
        products = Product.objects.all()
        categories = Category.objects.values("id", "parent", "name")
        result = cls.item_xml(products, categories, city_group_name)
        feeds_path = cls.get_feed_path(city_group_name)

        default_storage.save(name=feeds_path, content=ContentFile(result.encode('utf-8')))

        return feeds_path
    
    @classmethod
    def get_feed_path(cls, city_group_name: str) -> str:
        return os.path.join(settings.FEEDS_DIR, city_group_name, "feeds.xml")

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
            data["currencyId"] = "RUB"
            data["price"] = float(p.price)

        return data

    @classmethod
    def item_xml(cls, products, categories, city_group_name):
        yml_catalog = ET.Element(
            "yml_catalog", date=timezone.localtime(timezone.now()).date().isoformat()
        )
        shop = ET.SubElement(yml_catalog, "shop")

        name = ET.SubElement(shop, "name")
        company = ET.SubElement(shop, "company")

        if shop_name := get_shop_name():
            name.text = shop_name

        if company_name := Setting.objects.filter(predefined_key=SettingChoices.COMPANY_NAME).first():
            company.text = getattr(company_name, "value_string")

        url = ET.SubElement(shop, "url")

        base_url = f"{cls.schema}://"
        cg = CityGroup.objects.filter(name=city_group_name).first()
        if all((cg is not None, cg.main_city is not None)):
            city_domain = getattr(cg.main_city, "domain", None) or City.get_default_city().domain
            base_url = f"{cls.schema}://{city_domain}/"
        else:
            base_domain = get_base_domain() or City.get_default_city().domain
            base_url = f"{cls.schema}://{base_domain}/"

        url.text = base_url
        categories_elements = ET.SubElement(shop, "categories")
        offers = ET.SubElement(shop, "offers")

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

            item_url = urljoin(base_url, item.get_absolute_url())

            ET.SubElement(offer, "url").text = item_url
            ET.SubElement(offer, "description").text = item.description
            ET.SubElement(offer, "categoryId").text = str(item.category.id)
            ET.SubElement(offer, "vendor").text = item_extra_kwargs["vendor"]

            if value := item_extra_kwargs.get("sales_notes"):
                ET.SubElement(offer, "sales_notes").text = value

            if value := item_extra_kwargs.get("vendorCode"):
                ET.SubElement(offer, "vendorCode").text = value

            if value := item_extra_kwargs.get("country_of_origin"):
                ET.SubElement(offer, "country_of_origin").text = value

            if value := item_extra_kwargs.get("barcode"):
                ET.SubElement(offer, "barcode").text = value

            if value := item_extra_kwargs.get("weight"):
                ET.SubElement(offer, "weight").text = str(value)

            if value := item_extra_kwargs.get("price"):
                ET.SubElement(offer, "price").text = str(value)

            if value := item_extra_kwargs.get("picture"):
                ET.SubElement(offer, "picture").text = str(value)

            if value := item_extra_kwargs.get("currencyId"):
                ET.SubElement(offer, "currencyId").text = str(value)

            if value := item_extra_kwargs.get("dimensions"):
                ET.SubElement(offer, "dimensions").text = value

            ET.SubElement(offer, "cpa").text = str(item_extra_kwargs["cpa"]).lower()
            ET.SubElement(offer, "manufacturer_warranty").text = str(
                item_extra_kwargs["manufacturer_warranty"]
            ).lower()
            ET.SubElement(offer, "pickup").text = str(
                item_extra_kwargs["pickup"]
            ).lower()
            ET.SubElement(offer, "store").text = str(item_extra_kwargs["store"]).lower()

        return ET.tostring(yml_catalog, encoding="utf-8").decode("utf-8")
