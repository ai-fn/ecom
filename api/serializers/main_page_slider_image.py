from rest_framework import serializers
from shop.models import MainPageSliderImage


class MainPageSliderImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainPageSliderImage
        fields = ['id', 'order', 'link', 'image_text', 'button_text', "image"]
