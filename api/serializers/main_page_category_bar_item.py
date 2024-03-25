from shop.models import MainPageCategoryBarItem
from rest_framework import serializers


class MainPageCategoryBarItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MainPageCategoryBarItem
        fields = ["order", "link", "text"]
