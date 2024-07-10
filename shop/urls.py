from django.urls import path
from api.views import SimilarProducts


app_name = "shop"

urlpatterns = [
    path(
        "<int:product_id>/similar-products/",
        SimilarProducts.as_view({"get": "get"}),
        name="similar_products",
    ),
]
