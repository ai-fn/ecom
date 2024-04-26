from decimal import Decimal
import time
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.connections import connections

from loguru import logger
from typing import Any, Dict, Iterable
from django.conf import settings
import phonenumbers

from geopy.geocoders import Nominatim

from rest_framework import serializers

from account.models import City

from api.serializers import (
    PriceSerializer,
    ProductDocumentSerializer,
    CategoryDocumentSerializer,
    ReviewDocumentSerializer,
)
from shop.documents import CategoryDocument, ProductDocument, ReviewDocument
from shop.models import Category, Price, Product


class ValidatePhoneNumberMixin:

    def validate_phone_number(self, value):
        phone_number = value
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise serializers.ValidationError("Invalid phone number.")

        return value


class GeneralSearchMixin:

    def search(self, query: str, domain: str, exclude_: Iterable = None):
        default = {
            "product": {
                "queries": (
                    Q("wildcard", title={"value": f"*{query}*"}),
                    Q("wildcard", description={"value": f"*{query}*"}),
                ),
                "fields": (
                    "title^2",
                    "description",
                ),
                "indexes": (ProductDocument._index._name,),
            },
            "category": {
                "queries": (Q("wildcard", category__name={"value": f"*{query}*"}),),
                "fields": ("category__name",),
                "indexes": (CategoryDocument._index._name,),
            },
            "brand": {
                "queries": (Q("wildcard", brand__name={"value": f"*{query}*"}),),
                "fields": ("brand__name",),
                "index": 1,
            },
            "review": {
                "queries": (Q("wildcard", review={"value": f"*{query}*"}),),
                "fields": ("review",),
                "indexes": (ReviewDocument._index._name,),
            },
        }
        should, fields, indexes = [], [], []

        for k in default:
            if exclude_ is not None and k in exclude_:
                continue

            should.extend(default[k].get("queries", []))
            fields.extend(default[k].get("fields", []))
            indexes.extend(default[k].get("indexes", []))

        client = connections.get_connection()
        search = Search(
            using=client,
            index=indexes,
        )

        if exclude_ is not None and len(exclude_) > 0:
            search = search.extra(
                size=sum(
                    [
                        globals()[classname.capitalize()].objects.count()
                        for classname in default
                        if classname not in exclude_
                        and classname.capitalize() in globals()
                    ]
                )
            )

        if query:
            search = search.query(
                "bool",
                should=[
                    Q(
                        "multi_match",
                        query=query,
                        fields=["name^3", *fields],
                    ),
                    Q("wildcard", name={"value": f"*{query}*"}),
                    *should,
                ],
                minimum_should_match=1,
            )

        response = search.execute()

        if domain:
            city = City.objects.filter(domain=domain).first()
        else:
            city = None

        categorized_results = {
            "categories": [],
            "products": [],
            "reviews": [],
        }

        for hit in response:
            if hit.meta.index == ProductDocument._index._name:
                try:
                    product = Product.objects.get(id=hit.id)
                except Product.DoesNotExist:
                    logger.info(f"Product with hit {hit.id} not found")
                    continue

                if city:
                    price = Price.objects.filter(product=product, city_group__cities=city).first()
                    if price:
                        product_data = ProductDocumentSerializer(product).data
                        product_data["price"] = PriceSerializer(price).data
                        categorized_results["products"].append(product_data)
                else:
                    product_data = ProductDocumentSerializer(product).data
                    categorized_results["products"].append(product_data)
            elif hit.meta.index == CategoryDocument._index._name:
                category = Category.objects.get(id=hit.id)
                serializer = CategoryDocumentSerializer(category)
                categorized_results["categories"].append(serializer.data)
            elif hit.meta.index == ReviewDocument._index._name:
                serializer = ReviewDocumentSerializer(hit)
                categorized_results["reviews"].append(serializer.data)

        return categorized_results


class ValidateAddressMixin:

    def validate(self, data):

        data = super().validate(data)
        address_fields = ("region", "district", "city_name", "house", "street")

        if any([field in address_fields for field in data]):

            # Получаем поля адреса из тела запроса, если есть, иначе получаем из объекта пользователя
            address_values = [
                data.get(field, getattr(self.context["request"].user, field, "")) or ""
                for field in address_fields
            ]
            address = ", ".join(address_values[::-1])

            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(address)

            if not location:
                raise serializers.ValidationError(
                    "Указан несуществующий адрес"
                )

            logger.info(f"Найден адрес: {location.address}")
        return data


class TokenExpiredTimeMixin:

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        data["access_expired_at"] = (
            time.time() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        data["refresh_expired_at"] = (
            time.time() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )
        return data


class CityPricesMixin:

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {})
        kwargs["context"]["city_domain"] = getattr(self, "domain", "")
        kwargs["context"]["request"] = getattr(self, "request", "")
        return super().get_serializer(*args, **kwargs)


class SerializerGetPricesMixin:

    def get_city_price(self, obj) -> Decimal | None:
        city_domain = self.context.get("city_domain")
        if city_domain:
            try:
                c = City.objects.get(domain=city_domain)
            except City.DoesNotExist:
                logger.info(f"City with domain {city_domain} not found")
                return None
            
            price = Price.objects.filter(city_group__cities=c, product=obj).first()
            if price:
                return price.price
            
        logger.info(f"Price for city {c.name} by domain {city_domain} not found")
        return None

    def get_old_price(self, obj) -> Decimal | None:
        city_domain = self.context.get("city_domain")
        if city_domain:
            try:
                c = City.objects.get(domain=city_domain)
            except City.DoesNotExist:
                logger.info(f"City with domain {city_domain} not found")
                return None

            price = Price.objects.filter(city_group__cities=c, product=obj).first()
            if price:
                return price.old_price
            
        logger.info(f"Price for city {c.name} by domain {city_domain} not found")
        return None
