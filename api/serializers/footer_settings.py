from rest_framework import serializers

from shop.models import FooterSettings, FooterItem


class FooterSettingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FooterSettings
        fields = [
            "max_footer_items"
        ]


class FooterItemSerializer(serializers.ModelSerializer):

    footer_settings = FooterSettingSerializer()
    
    class Meta:
        model = FooterItem
        fields = [
            "order",
            "title",
            "link",
            "footer_settings",
        ]
