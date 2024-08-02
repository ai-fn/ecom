from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import SerializerMethodField
from api.serializers import ActiveModelSerializer, OpenGraphMetaSerializer

from shop.models import Page


class PageSerializer(ActiveModelSerializer):
    opengraph_metadata = SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "h1_tag",
            "description",
            "slug",
            "image",
            "opengraph_metadata",
        ]
        read_only_fields = ["slug", "id"]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.image:
            data["image"] = instance.image.url 
        if instance.opengraph_metadata.exists():
            data["opengraph_metadata"] = OpenGraphMetaSerializer(instance.opengraph_metadata.first()).data

        return data

    # @extend_schema_field(OpenGraphMetaSerializer)
    def get_opengraph_metadata(self, obj):
        if obj.opengraph_metadata.exists():
            return OpenGraphMetaSerializer(obj.opengraph_metadata.first()).data
        return None
