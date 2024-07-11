from shop.models import MainPageCategoryBarItem
from api.serializers import ActiveModelSerializer


class MainPageCategoryBarItemSerializer(ActiveModelSerializer):
    
    class Meta:
        model = MainPageCategoryBarItem
        fields = ["order", "link", "text"]
