from django.urls import path
from crm_integration.views import crm_webhook_view


urlpatterns = [
    path("<str:crm_name>/", crm_webhook_view, name="webhook-handler")
]
