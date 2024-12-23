import os
from PIL import Image

from django.conf import settings
from django.core.cache import cache

from loguru import logger


from account.models import City
from api.serializers import ActiveModelSerializer

from rest_framework.serializers import SerializerMethodField

from shop.utils import get_shop_name
from shop.services.metadata_service import MetaDataService
from shop.models import OpenGraphMeta, Setting, SettingChoices

META_IMAGE_PATH_CACHE_KEY = "META_IMAGE_PATH"
META_IMAGE_SIZE_REMINING_TIME = getattr(
    settings, "META_IMAGE_SIZE_REMINING_TIME", 3600 * 24
)  # время кеширования на сутки


class OpenGraphMetaSerializer(ActiveModelSerializer):

    images = SerializerMethodField()

    class Meta:
        model = OpenGraphMeta
        fields = [
            "title",
            "description",
            "keywords",
            "url",
            "images",
            "locale",
            "site_name",
        ]

    def get_images(self, obj: OpenGraphMeta) -> list:
        image = None
        result = []
        if (model := obj.content_type.lower()) and model in ("product", "category", "brand"):
            if model == "product":
                img_field_name = "catalog_image"
            elif model == "brand":
                img_field_name = "icon"
            else:
                img_field_name = "image"
            
            instance = obj.get_content_object()
            img_attr = getattr(instance, img_field_name)

            if img_attr.name:
                image = f"media/{img_attr.name}"
        else:
            image = self.get_meta_image()

        if image:
            result.append(image)

        return result


    def get_meta_image(self) -> dict[str, str] | None:
        result = None

        cached_data = cache.get(META_IMAGE_PATH_CACHE_KEY)
        if not cached_data:
            meta_image_setting = Setting.objects.filter(predefined_key=SettingChoices.OPEN_GRAPH_META_IMAGE).first()
            if not meta_image_setting:
                logger.info("Setting for openGraphMeta Image not found.")
            else:
                result = meta_image_setting.value_string
                cache.set(
                    META_IMAGE_PATH_CACHE_KEY, result, META_IMAGE_SIZE_REMINING_TIME
                )
        else:
            result = cached_data

        return result

    def to_representation(self, instance: OpenGraphMeta):
        data = super().to_representation(instance)
        query_params = getattr(self.context.get("request"), "query_params", {})

        city_domain = query_params.get("city_domain")
        fields = ("title", "keywords", "description")
        kwargs = {"city_domain": city_domain}

        if inst := self.context.get("instance"):
            kwargs["instance"] = inst
            data["content_type"] = inst._meta.model_name
            data["object_id"] = inst.id
        else:
            kwargs["instance"] = instance.get_content_object()

        fields = ("title", "keywords", "description")
        kwargs["fields"] = fields
        kwargs["meta_obj"] = instance

        result = MetaDataService.get_formatted_meta_tag_by_instance(**kwargs)
        for field in fields:
            data[field] = result.get(field)

        if not city_domain:
            city_domain = City.get_default_city().domain

        url = f"https://{city_domain}"
        if instance.content_type.lower() in ("product", "category"):
            url += f"/{instance.get_content_object().get_absolute_url()}/"
        else:
            url += data.get("url")

        keywords = (data.get("keywords") or "").split(";")
        site_name = data.get("site_name") or get_shop_name()

        if keywords:
            keywords = [x.strip() for x in keywords]

        return {
            "title": data.get("title"),
            "description": data.get("description"),
            "keywords": keywords,
            "openGraph": {
                "url": url,
                "siteName": site_name,
                "images": data.get("images"),
                "locale": data.get("locale"),
                "type": "website",
            },
            "alternates": {
                "canonical": url,
            },
        }
