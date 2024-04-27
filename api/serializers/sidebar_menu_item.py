from rest_framework.serializers import ModelSerializer, SerializerMethodField

from shop.models import SideBarMenuItem


class SideBarMenuItemSerializer(ModelSerializer):

    icon = SerializerMethodField()
    
    class Meta:
        model = SideBarMenuItem
        exclude = ["created_at", "updated_at"]
    
    def get_icon(self, obj):
        return obj.icon.url if obj.icon else None
