from django.urls import path
from shop.views import ProductListView, ProductDetail
from api.views import SimilarProducts

app_name = "shop"

urlpatterns = [
    path(
        "<int:product_id>/similar-products/",
        SimilarProducts.as_view(),
        name="similar_products",
    ),
    path(
        "<str:category_slug>/<slug:product_slug>/",
        ProductDetail.as_view(),
        name="product_detail",
    ),
    path(
        "<str:category_slug>/",
        ProductListView.as_view(),
        name="product_list_by_category",
    ),
]
