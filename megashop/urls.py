"""
URL configuration for megashop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import debug_toolbar

from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


from api.views import FeedsView
from shop.views import SitemapView



@login_required
def custom_schema_view(request, *args, **kwargs):
    return SpectacularAPIView.as_view()(request, *args, **kwargs)

@login_required
def custom_redoc_view(request, *args, **kwargs):
    return SpectacularRedocView.as_view(url_name="schema")(request, *args, **kwargs)

@login_required
def custom_swagger_view(request, *args, **kwargs):
    return SpectacularSwaggerView.as_view(url_name="schema")(request, *args, **kwargs)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api/", include("api.urls")),
        path("", include("django_prometheus.urls")),
        path("feeds.xml/", FeedsView.as_view(), name="product_feed"),
        path("account/", include("account.urls", namespace="account")),
        path("api/redoc/", never_cache(custom_redoc_view), name="redoc"),
        path("api/schema/", never_cache(custom_schema_view), name="schema"),
        path("api/swagger/", never_cache(custom_swagger_view), name="swagger-ui"),
        path("custom/sitemap.xml", view=SitemapView.as_view(), name="custom-sitemap"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
