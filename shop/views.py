from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from django.conf import settings

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.serializers.setting import SettingSerializer
from shop.models import Product, Category
from shop.sitemaps import ProductSitemap, CategorySitemap
from django.contrib.sitemaps.views import sitemap


sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
}


@extend_schema(
    tags=["Settings"],
    description="Получение карты сайта",
    summary="Получение карты сайта",
    parameters=[OpenApiParameter(description="Домен города", name="domain", required=False, type=str)],
    examples=[
        OpenApiExample(
            name="Sitemap Response Example",
            response_only=True,
            value="<?xml version='1.0' encoding='UTF-8'?>\
  <urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9' xmlns:xhtml='http://www.w3.org/1999/xhtml'>\
    <url>\
      <loc>https://krov.market/seriia-premium-3/zhelob-vodostochnyi-3-m-premium-plombir-113/</loc>\
      <lastmod>2024-03-18</lastmod>\
      <changefreq>always</changefreq>\
      <priority>0.8</priority>\
    </url>\
    <url>\
      <loc>https://krov.market/seriia-premium-3/zhelob-vodostochnyi-3-m-premium-shokolad-114/</loc>\
      <lastmod>2024-03-18</lastmod>\
      <changefreq>always</changefreq>\
      <priority>0.8</priority>\
    </url>\
    <url>\
      <loc>https://krov.market/seriia-standard-4/zhelob-vodostochnyi-3-m-standard-belyi-115/</loc>\
      <lastmod>2024-03-18</lastmod>\
      <changefreq>always</changefreq>\
      <priority>0.8</priority>\
    </url>",
        )
    ],
)
class CustomSitemap(APIView):
    permission_classes = [AllowAny]
    serializer_class = SettingSerializer

    def get(self, request):
        domain = request.query_params.get("domain")

        return sitemap(request, sitemaps={k: v(domain) for k, v in sitemaps.items()})
