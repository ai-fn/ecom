from django.db.models import Avg


class RatingMixin:

    def get_rating(self, obj) -> float:
        value = obj.reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0.0
        return round(value, 1)
