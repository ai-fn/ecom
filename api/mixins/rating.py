from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.fields import empty
from django.db.models import Avg



class RatingMixin(ModelSerializer):
    reviews_count = SerializerMethodField()
    rating = SerializerMethodField()

    class Meta:
        abstract = True

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        for field_name in ("rating", "reviews_count"):
            self.fields[field_name] = SerializerMethodField()

    def get_rating(self, obj) -> float:
        value = obj.reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0.0
        return round(value, 1)
    
    def get_reviews_count(self, obj) -> int:
        return obj.reviews.count()
