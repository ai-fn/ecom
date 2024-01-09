from django.shortcuts import render

from blog.models import Article
from shop.models import Category


def view_home(request):
    articles = Article.objects.order_by('created')
    categories = Category.objects.filter(parent=None)

    context = {
        'articles': articles,
        'categories': categories
    }

    return render(request, 'index.html', context)
