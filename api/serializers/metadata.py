from api.serializers import ActiveModelSerializer

from shop.models import ImageMetaData, OpenGraphMeta
from shop.services.metadata_service import MetaDataService


class ImageMetaDataSerializer(ActiveModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("id")
        data.pop("is_active")
        data['image'] = instance.image.url if instance.image else None
        data['url'] = data.pop("image")
        return data

    class Meta:
        model = ImageMetaData
        fields = [
            "id",
            "image",
            "width",
            "height",
        ]


class OpenGraphMetaSerializer(ActiveModelSerializer):

    images = ImageMetaDataSerializer(many=True, read_only=True, source="imagemetadata_set")
    
    class Meta:
        model = OpenGraphMeta
        fields = [
            "title",
            "description",
            "images",
            "keywords",
            "url",
            "locale",
            "site_name",
        ]

    def to_representation(self, instance: OpenGraphMeta):
        data = super().to_representation(instance)
        query_params = getattr(self.context.get("request"), "query_params", {})

        city_domain = query_params.get("city_domain")
        kwargs = {"city_domain": city_domain}

        if (inst := self.context.get("instance")):
            kwargs['instance'] = inst
            data['content_type'] = inst._meta.model_name
            data['object_id'] = inst.id
        else:
            kwargs['instance'] = instance.content_object
        
        fields = ("title", "keywords", "description")
        kwargs['fields'] = fields
        kwargs['meta_obj'] = instance

        result = MetaDataService.get_formatted_meta_tag_by_instance(**kwargs)
        for field in fields:
            data[field] = result.get(field)

        url = data.get('url')
        keywords = data.get('keywords').split(",")
        if keywords:
            keywords = [x.strip() for x in keywords]

        return {
            'title': data.get('title'),
            'description': data.get('description'),
            'keywords': keywords,
            'openGraph': {
                'url': url,
                'siteName': data.get('site_name'),
                'images': data.get('images'),
                'locale': data.get('locale'),
                'type': "website",
            },
            'alternates': {
                'canonical': url,
            }
        }
