from rest_framework import serializers
from blog.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id",
            "name",
            "email",
            "message",
        ]
