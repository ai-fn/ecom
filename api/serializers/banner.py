from api.serializers import ActiveModelSerializer
from shop.models import Banner


class BannerSerializer(ActiveModelSerializer):

    class Meta:
        model = Banner
        fields = [
            "id",
            "order",
            "link",
            "title",
            "description",
            "button_text",
            "image",
            "tiny_image",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = instance.image.url if instance.image else None
        data["tiny_image"] = instance.tiny_image.url if instance.image else None
        return data
