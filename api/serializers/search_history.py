from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from account.models import CustomUser
from shop.models import SearchHistory


class SearchHistorySerializer(ModelSerializer):

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = SearchHistory
        fields = ["title", "user_id"]
