from rest_framework.serializers import ModelSerializer, SerializerMethodField, ImageField

from shop.models import ImageMetaData, OpenGraphMeta


class ImageMetaDataSerializer(ModelSerializer):

    image = ImageField(write_only=True)
    image_url = SerializerMethodField(read_only=True)

    def get_image_url(self, obj) -> str:
        return obj.image.url if obj.image else None

    class Meta:
        model = ImageMetaData
        fields = [
            "id",
            "image",
            "image_url",
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
