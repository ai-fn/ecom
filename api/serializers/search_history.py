from api.serializers import ActiveModelSerializer
from account.models import CustomUser
from shop.models import SearchHistory
from rest_framework import serializers


class SearchHistorySerializer(ActiveModelSerializer):

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = SearchHistory
        fields = [
            "id",
            "title",
            "user_id",
        ]
