from django.http import FileResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.files.storage import default_storage

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from account.models import City
from shop.services import SitemapService
from api.serializers import SettingSerializer


@extend_schema(
    tags=["Settings"],
    description="Получение карты сайта",
    summary="Получение карты сайта",
    parameters=[
        OpenApiParameter(
            description="Домен города",
            name="domain",
            required=True,
            type=str,
        )
    ],
    examples=[
        OpenApiExample(
            name="Sitemap Response Example",
            response_only=True,
            value="<?xml version='1.0' encoding='UTF-8'?>\
  <urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9' xmlns:xhtml='http://www.w3.org/1999/xhtml'>\
    <url>\
      <loc>https://domain.com/seriia-premium-3/zhelob-vodostochnyi-3-m-premium-plombir-113/</loc>\
      <lastmod>2024-03-18</lastmod>\
      <changefreq>always</changefreq>\
      <priority>0.8</priority>\
    </url>\
    <url>\
      <loc>https://domain.com/seriia-premium-3/zhelob-vodostochnyi-3-m-premium-shokolad-114/</loc>\
      <lastmod>2024-03-18</lastmod>\
      <changefreq>always</changefreq>\
      <priority>0.8</priority>\
    </url>\
    <url>\
      <loc>https://domain.com/seriia-standard-4/zhelob-vodostochnyi-3-m-standard-belyi-115/</loc>\
      <lastmod>2024-03-18</lastmod>\
      <changefreq>always</changefreq>\
      <priority>0.8</priority>\
    </url>",
        )
    ],
)
class SitemapView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SettingSerializer

    @method_decorator(cache_page(120 * 60))
    def get(self, request):
        domain = request.query_params.get("domain")
        if not domain:  
            return HttpResponse(status=404)

        c = City.objects.filter(domain=domain).first()
        if not c:
            return HttpResponse(status=404)

        path = SitemapService.get_xml_file_path(c.name)
        try:
            with default_storage.open(path, "rb") as file:
                response = FileResponse(file, content_type="application/xml")
                response["Content-Disposition"] = 'attachment; filename="sitemap.xml"'
                return response
        except FileNotFoundError:
            return HttpResponse(status=404)
