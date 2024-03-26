from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.conf import settings

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.serializers.setting import SettingSerializer
from blog.sitemaps import ArticleSitemap
from shop.forms import ReviewForm
from shop.models import Product, Category
from shop.sitemaps import ProductSitemap, CategorySitemap
from django.contrib.sitemaps.views import sitemap


sitemaps = {
    "articles": ArticleSitemap,
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


class ProductListView(ListView):
    paginate_by = settings.PAGINATE_BY
    context_object_name = "products_list"

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])

        # Получаем все подкатегории для выбранной категории
        categories = self.category.get_descendants(include_self=True)

        # Фильтруем продукты по выбранной категории и всем её подкатегориям
        return Product.objects.filter(Q(category__in=categories)).select_related(
            "category"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProductDetail(DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        context["form"] = ReviewForm
        return context

    def post(self, request, *args, **kwargs):
        form = ReviewForm(request.POST, request.FILES)
        self.object = super(ProductDetail, self).get_object()
        context = super(ProductDetail, self).get_context_data()
        context["form"] = ReviewForm
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.product = self.object
            new_review.save()

        else:
            context["form"] = form

        return self.render_to_response(context=context)
