from django.http import JsonResponse
from django.shortcuts import render
from loguru import logger

from shop.models import Product

# Create your views here.


def search_view(request):
    query = request.GET.get("query", "")
    if query:
        products = Product.objects.filter(title__icontains=query)
        results = [
            {
                "title": product.title,
                "url": product.get_absolute_url(),
                "image_url": product.image.url if product.image else None,
            }
            for product in products
        ]
        return JsonResponse({"results": results})
    return JsonResponse({"results": []})
