import os
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.syndication.views import Feed

from account.models import City
from shop.utils import get_base_domain, get_shop_name
from shop.models import Category, Product, Setting, SettingChoices


class FeedsService(Feed):
    """
    Сервис для генерации XML-фидов для товарных предложений.
    """

    schema = "https"
    city_group_name = None

    @classmethod
    def collect_feeds(cls, city_group_name: str) -> str:
        """
        Генерирует XML-фид для указанной группы городов.

        :param city_group_name: Название группы городов.
        :return: Путь к сохраненному фиду.
        """
        cls.city_group_name = city_group_name
        products = Product.objects.all()
        categories = Category.objects.values("id", "parent", "name")
        result = cls.item_xml(products, categories, city_group_name)
        feeds_path = cls.get_feed_path(city_group_name)

        default_storage.save(name=feeds_path, content=ContentFile(result.encode("utf-8")))
        return feeds_path

    @classmethod
    def get_feed_path(cls, city_group_name: str) -> str:
        """
        Возвращает путь для сохранения XML-фида.

        :param city_group_name: Название группы городов.
        :return: Путь для сохранения фида.
        """
        return os.path.join(settings.FEEDS_DIR, city_group_name, "feeds.xml")

    @classmethod
    def item_extra_kwargs(cls, item: Product) -> dict:
        """
        Генерирует дополнительные параметры для товаров.

        :param item: Экземпляр товара.
        :return: Словарь с дополнительными параметрами.
        """
        data = {
            "delivery": True,
            "name": item.title,
            "available": item.is_active,
            "pickup": True,
            "country_of_origin": "Россия",
            "weight": 0.5,
            "categoryId": item.category.id,
            "description": item.description,
            "barcode": "barcode",
            "vendorCode": item.article,
            "vendor": item.brand.name if item.brand else "Бренд",
            "manufacturer_warranty": True,
            "dimensions": "10.0/20.0/30.0",
            "store": True,
            "cpa": 1,
            "sales_notes": "Минимальная партия заказа - 1 шт.",
        }
        if item.catalog_image and hasattr(item.catalog_image, "url"):
            data["picture"] = item.catalog_image.url

        if p := item.prices.filter(city_group__name=cls.city_group_name).first():
            data["currencyId"] = "RUB"
            data["price"] = float(p.price)

        return data

    @classmethod
    def item_xml(cls, products, categories, city_name: str) -> str:
        """
        Генерирует XML-документ для товаров и категорий.

        :param products: Список товаров.
        :param categories: Список категорий.
        :param city_name: Название города.
        :return: XML-документ в виде строки.
        """
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
        city = City.objects.filter(name=city_name).first()

        if city is not None:
            base_url = f"{cls.schema}://{city.domain}/"
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

            ET.SubElement(categories_elements, "category", **ctg_kwargs).text = category["name"]

        for item in products:
            item_extra_kwargs = cls.item_extra_kwargs(item)
            offer = ET.SubElement(offers, "offer", id=str(item.id), available="true")

            ET.SubElement(offer, "name").text = item.title
            item_url = urljoin(base_url, item.get_absolute_url())
            ET.SubElement(offer, "url").text = item_url
            ET.SubElement(offer, "description").text = item.description
            ET.SubElement(offer, "categoryId").text = str(item.category.id)
            ET.SubElement(offer, "vendor").text = item_extra_kwargs["vendor"]

            for field in ["sales_notes", "vendorCode", "country_of_origin", "barcode", "weight", "price", "picture", "currencyId", "dimensions"]:
                if value := item_extra_kwargs.get(field):
                    ET.SubElement(offer, field).text = str(value)

            for bool_field in ["cpa", "manufacturer_warranty", "pickup", "store"]:
                ET.SubElement(offer, bool_field).text = str(item_extra_kwargs[bool_field]).lower()

        return ET.tostring(yml_catalog, encoding="utf-8").decode("utf-8")
