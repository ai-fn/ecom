import os
from PIL import Image

from django.conf import settings
from django.core.cache import cache

from loguru import logger


from account.models import City
from api.serializers import ActiveModelSerializer

from rest_framework.serializers import SerializerMethodField

from shop.models import OpenGraphMeta, Setting, SettingChoices
from shop.services.metadata_service import MetaDataService

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

    def get_images(self, obj) -> list:
        image = None
        result = []
        if (model := obj.content_type.model) and model in ("product", "category", "brand"):
            if model == "product":
                img_field_name = "catalog_image"
            elif model == "brand":
                img_field_name = "icon"
            else:
                img_field_name = "image"
            
            img_attr = getattr(obj.content_object, img_field_name)

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

        kwargs["fields"] = fields
        kwargs["meta_obj"] = instance
        kwargs["instance"] = instance.content_object

        result = MetaDataService.get_formatted_meta_tag_by_instance(**kwargs)
        for field in fields:
            data[field] = result.get(field)

        if not city_domain:
            city_domain = City.get_default_city().domain

        url = f"https://{city_domain}"
        if instance.content_type.model in ("product", "category"):
            url += f"/{instance.content_object.get_absolute_url()}/"
        else:
            url += data.get("url")

        keywords = (data.get("keywords") or "").split(";")
        site_name = data.get("site_name") or os.environ.get("SHOP_NAME", "site name")

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
