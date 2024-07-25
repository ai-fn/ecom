from rest_framework import serializers
from blog.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):

    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            "id",
            "name",
            "email",
            "message",
            "status",
            "status_display",
        ]

    def get_status_display(self, obj) -> str:
        return obj.get_status_display()
