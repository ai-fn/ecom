from rest_framework.exceptions import ValidationError

from shop.models import Review
from api.serializers import UserReviewSerializer, ActiveModelSerializer


class ReviewSerializer(ActiveModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "rating",
            "review",
            "created_at",
        ]
        extra_kwargs  = {"user": {"required": False}}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserReviewSerializer(instance.user).data

        return data
    
    def save(self, **kwargs):
        user = self.validated_data.get("user")
        if not user:
            user = getattr(self.context.get("request"), "user", None)
            if not user:
                raise ValidationError("'user' attribute is required", "required")
            
            self.validated_data["user"] = user

        return super().save(**kwargs)
