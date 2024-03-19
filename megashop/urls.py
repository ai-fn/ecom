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

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from blog import views
from search import views as search_views
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

from shop.views import CustomSitemap, sitemaps



@login_required
def custom_swagger_view(request, *args, **kwargs):
    return SpectacularSwaggerView.as_view(url_name="schema")(request, *args, **kwargs)


@login_required
def custom_redoc_view(request, *args, **kwargs):
    return SpectacularRedocView.as_view(url_name="schema")(request, *args, **kwargs)


@login_required
def custom_schema_view(request, *args, **kwargs):
    return SpectacularAPIView.as_view()(request, *args, **kwargs)


urlpatterns = (
    [
        path("account/", include("account.urls")),
        path("admin/", admin.site.urls),
        path("", views.view_home, name="home"),
        path("search/", view=search_views.search_view, name="search"),
        path("feeds/products/feeds.xml", ProductsFeed(), name='prods-feeds'),
        path("feeds/categories/feeds.xml", CategoriesFeed(), name='catg-feeds'),
        path("feeds.xml/", AllFeedsXMLAPIView.as_view(), name="all-feeds"),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path("custom/sitemap.xml", view=CustomSitemap.as_view(), name="custom-sitemap"),
        path("api/", include("api.urls")),
        path("api/schema/", never_cache(custom_schema_view), name="schema"),
        path("api/swagger/", never_cache(custom_swagger_view), name="swagger-ui"),
        path("api/redoc/", never_cache(custom_redoc_view), name="redoc"),
        path("", include("django_prometheus.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
