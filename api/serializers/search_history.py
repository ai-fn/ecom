from rest_framework.serializers import ModelSerializer
from shop.models import SearchHistory


class SearchHistorySerializer(ModelSerializer):
    
    class Meta:
        model = SearchHistory
        fields = ["title"]
