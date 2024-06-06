import time
import phonenumbers

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError 

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from decimal import Decimal
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.connections import connections

from loguru import logger
from typing import Any, Dict, Iterable
from django.conf import settings

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

from account.models import City

from api.serializers import (
    PriceSerializer,
    ProductDocumentSerializer,
    CategoryDocumentSerializer,
    ReviewDocumentSerializer,
)
from shop.documents import CategoryDocument, ProductDocument, ReviewDocument
from shop.models import Category, Price, Product, SearchHistory


class ValidatePhoneNumberMixin:

    def validate_phone_number(self, value):
        phone_number = value
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Invalid phone number.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError("Invalid phone number.")

        return value


class GeneralSearchMixin:

    def g_search(self, query: str, domain: str, exclude_: Iterable = None):
        if self.request.user.is_authenticated:
            SearchHistory.objects.get_or_create(title=query, user=self.request.user)

        exclude_ = exclude_ or []
        default = {
            "product": {
                "queries": (
                    Q("wildcard", title={"value": f"*{query}*"}),
                    Q("wildcard", description={"value": f"*{query}*"}),
                ),
                "fields": ("title^2", "description"),
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

        for key, config in default.items():
            if key not in exclude_:
                should.extend(config.get("queries", []))
                fields.extend(config.get("fields", []))
                indexes.extend(config.get("indexes", []))

        client = connections.get_connection()
        search = Search(using=client, index=indexes)

        if exclude_:
            search = search.extra(size=sum(
                [
                    globals()[classname.capitalize()].objects.count()
                    for classname in default
                    if classname not in exclude_ and classname.capitalize() in globals()
                ]
            ))

        if query:
            search = search.query(
                "bool",
                should=[
                    Q("multi_match", query=query, fields=["name^3", *fields]),
                    Q("wildcard", name={"value": f"*{query}*"}),
                    *should,
                ],
                minimum_should_match=1,
            )

        response = search.execute()

        city = City.objects.filter(domain=domain).first() if domain else None
        categorized_results = {"categories": [], "products": [], "reviews": []}

        for hit in response:
            if hit.meta.index == ProductDocument._index._name:
                self.process_product(hit, city, categorized_results)
            elif hit.meta.index == CategoryDocument._index._name:
                self.process_category(hit, categorized_results)
            elif hit.meta.index == ReviewDocument._index._name:
                self.process_review(hit, categorized_results)

        return categorized_results

    def process_product(self, hit, city, categorized_results):
        try:
            product = Product.objects.get(id=hit.id)
        except Product.DoesNotExist:
            logger.info(f"Product with hit {hit.id} not found")
            return

        product_data = ProductDocumentSerializer(product).data
        if city:
            price = Price.objects.filter(product=product, city_group__cities=city).first()
            if price:
                product_data["price"] = PriceSerializer(price).data
        categorized_results["products"].append(product_data)

    def process_category(self, hit, categorized_results):
        try:
            category = Category.objects.get(id=hit.id)
        except Category.DoesNotExist:
            logger.info(f"Category with hit {hit.id} not found")
            return

        serializer = CategoryDocumentSerializer(category)
        categorized_results["categories"].append(serializer.data)

    def process_review(self, hit, categorized_results):
        serializer = ReviewDocumentSerializer(hit)
        categorized_results["reviews"].append(serializer.data)


class ValidateAddressMixin:

    def validate(self, data):

        def split_address(address):
            parts = set()
            for part in address.split(','):
                parts.update(part.strip().split())
            return parts


        data = super().validate(data)
        address = data.get("address")
        if not address:
            return ValidationError()
        
        try:

            geolocator = Nominatim(user_agent="my_geocoder")
            locations = geolocator.geocode(address, exactly_one=False)
            if not locations:
                raise ValidationError("Указан несуществующий адрес")
            
            user_address_parts = split_address(address.lower())
            matches = {}

            for location in locations:
                found_address_parts = split_address(location.address.lower())
                common_parts = user_address_parts.intersection(found_address_parts)
                match_score = len(common_parts) / len(user_address_parts)
                matches[location.address] = match_score
            
            max_match_address = max(matches, key=matches.get)
            max_match_score = matches[max_match_address]

            if max_match_score < 0.8:
                raise ValidationError("Адрес найден, но значительно отличается от введенного.")

            data['address'] = max_match_address

            logger.info(f"Найден адрес: {max_match_address}")
        except GeocoderServiceError as e:
            raise ValidationError(f"{str(e)}\nОшибка службы геокодирования. Пожалуйста, повторите попытку позже.")
        return data


class GenerateCodeMixin:

    def _generate_code(self, length=4):
        from string import digits
        from random import choices

        return "".join(choices(digits, k=length))


class SendVirifyEmailMixin(GenerateCodeMixin):

    _EMAIL_CACHE_PREFIX = getattr(settings, "EMAIL_CACHE_PREFIX", "EMAIL_CACHE_PREFIX")
    _EMAIL_CACHE_LIFE_TIME = getattr(settings, "EMAIL_CACHE_LIFE_TIME", 60 * 60)
    _EMAIL_CACHE_REMAINING_TIME = getattr(settings, "EMAIL_CACHE_REMAINING_TIME", 60 * 2)


    def _get_code(self, email: str):
        return cache.get(key=self._get_cache_key(email))

    def _get_cache_key(self, email: str) -> str:
        return f"{self._EMAIL_CACHE_PREFIX}_{email}"

    def _invalidate_cache(self, email: str) -> None:
        cache.delete(self._get_cache_key(email))

    def _generate_message(
        self,
        request,
        user,
        email,
    ):
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        code = self._generate_code()
        expiration_time = time.time() + self._EMAIL_CACHE_REMAINING_TIME
        cache.set(
            key=self._get_cache_key(email),
            value={
                "expiration_time": expiration_time,
                "code": code,
            },
            timeout=self._EMAIL_CACHE_LIFE_TIME,
        )

        context = {
            "email": email,
            "domain": domain,
            "site_name": site_name,
            "user": user,
            "code": code,
            "protocol": ["https", "http"][settings.DEBUG],
        }
        return context, expiration_time

    def _send_confirm_email(
        self, request, user, email, email_template_name="email/index.html"
    ):
        cached_data = self._get_code(email)
        if cached_data:
            expiration_time = cached_data.get("expiration_time")
            remaining_time = expiration_time - time.time()
            if remaining_time >= 0:
                return Response(
                        {
                            "message": f"Please wait. Time remaining: {int(remaining_time) // 60:02d}:{int(remaining_time) % 60:02d}",
                            "expiration_time": expiration_time
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )

        context, expiration_time = self._generate_message(request, user, email)
        body = render_to_string(email_template_name, context)

        result = send_mail(
            _("Confrim email"),
            "",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True,
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD,
            html_message=body,
        )
        if result:
            return Response(
                {"message": "Message sent successfully", "expiration_time": expiration_time}, status=HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Message sent failed"}, status=HTTP_400_BAD_REQUEST
            )


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

        return None
