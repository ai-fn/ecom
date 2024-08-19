from PIL import Image
from django.conf import settings
from loguru import logger

from django.core.cache import cache

from api.serializers import ActiveModelSerializer

from rest_framework.serializers import Serializer, CharField

from shop.models import OpenGraphMeta, Setting, SettingChoices
from shop.services.metadata_service import MetaDataService

META_IMAGE_PATH_CACHE_KEY = "META_IMAGE_PATH"
META_IMAGE_SIZE_CACHE_KEY = "META_IMAGE_SIZE"
META_IMAGE_SIZE_REMINING_TIME = getattr(
    settings, "META_IMAGE_SIZE_REMINING_TIME", 3600 * 24
)  # время кеширования на сутки


class ImageMetaDataSerializer(Serializer):
    image = CharField()


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = path if (path := data["image"]) and path.startswith("/") else "/" + path
        image_size = cache.get(META_IMAGE_SIZE_CACHE_KEY)
        if image_size:

            try:
                image_path = settings.BASE_DIR / data["image"][1:]
                with Image.open(image_path) as image:
                    image_size = {"width": image.width, "height": image.height}
                    cache.set(META_IMAGE_SIZE_CACHE_KEY, image_size, META_IMAGE_SIZE_REMINING_TIME)

            except Exception as e:
                image_size = {"width": None, "height": None}
                logger.error(f"Error while open openGraphMeta image: {str(e)}")
        
        data.update(image_size)

        return data


class OpenGraphMetaSerializer(ActiveModelSerializer):

    class Meta:
        model = OpenGraphMeta
        fields = [
            "title",
            "description",
            "keywords",
            "url",
            "locale",
            "site_name",
        ]
    
    def get_meta_image(self) -> dict[str, str] | None:
        result = None
        cached_data = cache.get(META_IMAGE_PATH_CACHE_KEY)
        if not cached_data:
            result = cached_data

        else:
            meta_image_setting = Setting.objects.filter(predefined_key=SettingChoices.OPEN_GRAPH_META_IMAGE).first()
            if not meta_image_setting:
                logger.info("Setting for openGraphMeta Image not found.")
            else:
                result = {"image": meta_image_setting.value_string}
                cache.set(
                    META_IMAGE_PATH_CACHE_KEY, result, META_IMAGE_SIZE_REMINING_TIME
                )

        return result

    def to_representation(self, instance: OpenGraphMeta):
        data = super().to_representation(instance)
        query_params = getattr(self.context.get("request"), "query_params", {})

        city_domain = query_params.get("city_domain")
        kwargs = {"city_domain": city_domain}

        if inst := self.context.get("instance"):
            kwargs["instance"] = inst
            data["content_type"] = inst._meta.model_name
            data["object_id"] = inst.id
        else:
            kwargs["instance"] = instance.content_object

        fields = ("title", "keywords", "description")
        kwargs["fields"] = fields
        kwargs["meta_obj"] = instance

        result = MetaDataService.get_formatted_meta_tag_by_instance(**kwargs)
        for field in fields:
            data[field] = result.get(field)

        url = data.get("url")
        keywords = data.get("keywords").split(",")
        if keywords:
            keywords = [x.strip() for x in keywords]
        
        images = []
        meta_image_data = self.get_meta_image()
        if meta_image_data:
            images.append(ImageMetaDataSerializer(meta_image_data).data)

        return {
            "title": data.get("title"),
            "description": data.get("description"),
            "keywords": keywords,
            "openGraph": {
                "url": url,
                "siteName": data.get("site_name"),
                "images": images,
                "locale": data.get("locale"),
                "type": "website",
            },
            "alternates": {
                "canonical": url,
            },
        }
