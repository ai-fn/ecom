from django.urls import path, include


urlpatterns = [
    path("crm-webhook/", include("crm_integration.urls")),
]