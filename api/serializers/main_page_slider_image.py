from api.serializers import ActiveModelSerializer
from shop.models import MainPageSliderImage
from rest_framework import serializers


class MainPageSliderImageSerializer(ActiveModelSerializer):

    image = serializers.SerializerMethodField()
    tiny_image = serializers.SerializerMethodField()

    class Meta:
        model = MainPageSliderImage
        fields = ['id', 'order', 'link', 'title', "description",  'button_text', "image", "thumb_img", "tiny_image",]
    
    def get_image(self, obj) -> str | None:
        return obj.image.url if obj.image else None
    
    def get_tiny_image(self, obj) -> str | None:
        return obj.tiny_image.url if obj.tiny_image else None
