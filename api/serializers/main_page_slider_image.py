from rest_framework import serializers
from shop.models import MainPageSliderImage


class MainPageSliderImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainPageSliderImage
        fields = ['id', 'order', 'link', 'title', "description",  'button_text', "image"]
