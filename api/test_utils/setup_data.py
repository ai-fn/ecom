import os, json
from decimal import Decimal
from typing import Iterable

from django.test import TestCase
from django.utils.text import slugify
from unidecode import unidecode
from shop.models import (
    Product,
    Category,
    Brand,
    Price,
    Characteristic,
    CharacteristicValue,
    SearchHistory,
)
from account.models import City, CityGroup, CustomUser


class SetupTestData:

    def __init__(self, *args, **kwargs):
        self.categories = None
        self.brands = None
        self.products = None
        fd = os.path.dirname(__file__)
        with open(f"{fd}/test_data.json") as file:
            self.data = json.loads(file.read())


    def setup_test_data(self):
        for brand_name in self.data:
            b = self.setup_brand(brand_name, order=self.data[brand_name]["order"])
            for ctg_name in self.data[brand_name]["category"]:
                ctg_data = self.data[brand_name]["category"][ctg_name].copy()
                products_data = ctg_data.pop("products")
                c = self.setup_category(ctg_name, **ctg_data)
                for prod_dict in products_data:
                    prod_dict.pop("chars")
                    prod_dict.pop("prices")
                    self.setup_product(**prod_dict, category=c, brand=b)


    def setup_prices(self):
        result = []
        for brand_name in self.data:
            for ctg_name in self.data[brand_name]["category"]:
                ctg_data = self.data[brand_name]["category"][ctg_name].copy()
                products_data = ctg_data.pop("products")
                for prod_dict in products_data:
                    p_data = prod_dict.copy()
                    prices_data = p_data.pop("prices")
                    for price_data in prices_data:
                        prod = Product.objects.get(title=prod_dict["title"])
                        cg, _ = self.setup_city_group(
                            name=price_data.pop("city_group__name")
                        )
                        price = self.setup_price(
                            product=prod, city_group=cg, **price_data
                        )
                        result.append(price)
        return result


    def setup_product(self, title, article, category, **kwargs):
        p, _ = Product.objects.get_or_create(title=title, article=article, category=category, **kwargs)
        return p


    def setup_chars(self):
        result = {"chars": [], "values": []}
        for brand_name in self.data:
            for ctg_name in self.data[brand_name]["category"]:
                ctg_data = self.data[brand_name]["category"][ctg_name].copy()
                c = Category.objects.get(name=ctg_name)
                products_data = ctg_data.pop("products")
                for prod_dict in products_data:
                    p_data = prod_dict.copy()
                    chars_data = p_data.pop("chars")
                    prod = Product.objects.get(title=prod_dict["title"])
                    for char in chars_data:
                        char_vals_data = char.pop("values")
                        char = self.setup_characteristic(categories=(c,), **char)
                        result["chars"].append(char)
                        for char_val in char_vals_data:
                            char_value = self.setup_characteristic_value(prod, char, **char_val)

                            result["values"].append(char_value)

        return result

    def setup_price(self, product, city_group_name, price, **kwargs):
        if not (cg := kwargs.get("city_group")):
            cg, _ = CityGroup.objects.get_or_create(name=city_group_name)

        price = Decimal(price)
        if op := kwargs.get("old_price"):
            kwargs["old_price"] = Decimal(op)

        p, _ = Price.objects.get_or_create(product=product, city_group=cg, price=price,  **kwargs)
        return p

    def setup_characteristic(
        self, name, categories: Iterable[int] = None, **kwargs
    ):
        if categories is None:
            categories = ()

        c, _ = Characteristic.objects.get_or_create(name=name, **kwargs)
        c.categories.add(*categories)
        return c

    def setup_characteristic_value(self, product, characteristic, value, **kwargs):
        cv, _ = CharacteristicValue.objects.get_or_create(
            product=product,
            characteristic=characteristic,
            defaults={"value": value},
            **kwargs,
        )
        return cv

    def setup_city_group(self, name, **kwargs):
        cg, _ = CityGroup.objects.get_or_create(name=name, **kwargs)
        return cg

    def setup_city(self, name, city_group: CityGroup = None, **kwargs):
        c, _ = City.objects.get_or_create(name=name, city_group=city_group, **kwargs)
        return c

    def setup_custom_user(self, username, email, password, **kwargs):
        cu, _ = CustomUser.objects.get_or_create(
            username=username, email=email, password=password, **kwargs
        )
        return cu

    def setup_search_history(self, title, user, **kwargs):
        sh, _ = SearchHistory.objects.get_or_create(title=title, user=user, **kwargs)
        return sh

    def setup_brand(self, name, **kwargs):
        b, _ = Brand.objects.get_or_create(name=name, **kwargs)
        return b

    def setup_category(self, name, **kwargs):
        c, _ = Category.objects.get_or_create(name=name, **kwargs)
        return c
