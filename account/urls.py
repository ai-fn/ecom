from django.urls import path, include

from account.views import AccountInfoViewSet

app_name = "account"

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('get-info/', AccountInfoViewSet.as_view({'get': "retrieve"}), name="account-retrieve"),
    path('update-info/', AccountInfoViewSet.as_view({'patch': "partial_update"}), name="account-patch"),
    path('verify_email/', AccountInfoViewSet.as_view({'post': "verify_email"}), name="account-post"),
    path('resend_verify_email/', AccountInfoViewSet.as_view({'get': "resend_verify_email"}), name="account-post_resend"),
]