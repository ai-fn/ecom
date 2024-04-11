from rest_framework import serializers
from shop.models import MainPageSliderImage


class MainPageSliderImageSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = MainPageSliderImage
        fields = ['id', 'order', 'link', 'title', "description",  'button_text', "image"]
    
    def get_image(self, obj) -> str | None:
        return obj.image.url if obj.url else None
