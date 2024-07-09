from rest_framework.serializers import ModelSerializer, SerializerMethodField, ImageField

from shop.models import ImageMetaData, OpenGraphMeta


class ImageMetaDataSerializer(ModelSerializer):

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


class OpenGraphMetaSerializer(ModelSerializer):

    images = ImageMetaDataSerializer(many=True, read_only=True, source="imagemetadata_set")
    
    def to_representation(self, instance: OpenGraphMeta):
        data = super().to_representation(instance)
        return {
            'title': data['title'],
            'description': data['description'],
            'OpenGraph': {
                'url': data['url'],
                'siteName': data['site_name'],
                'images': data['images'],
                'locale': data['locale'],
                'type': "website",
            },
        }
    
    class Meta:
        model = OpenGraphMeta
        exclude = []
