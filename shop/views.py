from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from shop.forms import ReviewForm
from shop.models import Product, Category

from django.db.models import Q


class ProductListView(ListView):
    paginate_by = 9
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
