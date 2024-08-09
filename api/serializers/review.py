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

    def validate(self, data):
        user = self.context.get('request').user

        if user.is_anonymous:
            raise ValidationError({"user": "User must be logged in to submit a review."})

        product = data.get('product')

        if not product:
            raise ValidationError({"product": "Product must be specified."})

        if not user.is_staff:
            purchases = user.customer.prefetch_related('products').values_list('products', flat=True)
            if product.id not in purchases:
                raise ValidationError("You can only leave a review for products you have purchased.")

        return data

    
    def save(self, **kwargs):
        user = self.validated_data.get("user")
        if not user:
            user = self.context["request"].user            
            self.validated_data["user"] = user

        return super().save(**kwargs)
