from api.serializers import ActiveModelSerializer
from rest_framework.serializers import ImageField

from shop.models import ImageMetaData, OpenGraphMeta


class ImageMetaDataSerializer(ActiveModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.url if instance.image else None
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
            "url",
            "locale",
            "site_name",
        ]

    def to_representation(self, instance: OpenGraphMeta):
        data = super().to_representation(instance)
        return {
            'title': data.get('title'),
            'description': data.get('description'),
            'OpenGraph': {
                'url': data.get('url'),
                'siteName': data.get('site_name'),
                'images': data.get('images'),
                'locale': data.get('locale'),
                'type': "website",
            },
        }
