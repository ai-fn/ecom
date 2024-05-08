from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from shop.models import ImageMetaData, OpenGraphMeta


class ImageMetaDataSerializer(ModelSerializer):

    open_graph_meta = PrimaryKeyRelatedField(write_only=True)
    class Meta:
        model = ImageMetaData
        exclude = ["open_graph_meta"]


class OpenGraphMetaSerializer(ModelSerializer):
    
    images = ImageMetaDataSerializer(many=True)

    class Meta:
        model = OpenGraphMeta
        exclude = []
    
    def to_representation(self, obj: OpenGraphMeta):
        return {
            'title': obj.title,
            'description': obj.description,
            'OpenGraph': {
                'title': obj.title,
                'description': obj.description,
                'url': obj.url,
                'siteName': obj.site_name,
                'images': obj.images,
                'locale': obj.locale,
                'type': obj.type,
            }
        }
