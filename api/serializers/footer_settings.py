from api.serializers import ActiveModelSerializer
from shop.models import FooterItem


class FooterItemSerializer(ActiveModelSerializer):
    
    class Meta:
        model = FooterItem
        fields = [
            "id",
            "column",
            "order",
            "title",
            "link",
        ]
