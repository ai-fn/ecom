from .models import Category


def shop(request):
    return {"shop": Category.objects.all()}
