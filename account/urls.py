from django.urls import path, include

from account import views

app_name = "account"

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('get-info/', views.AccountInfoViewSet.as_view({'get': "retrieve"}), name="account-retrieve"),
    path('update-info/', views.AccountInfoViewSet.as_view({'patch': "partial_update"}), name="account-patch"),
    path('register/', views.Register.as_view(), name='register'),
    path('verify-email/<str:uid64>/<str:token>/', views.EmailVerifyView.as_view(), name='verify-email'),
]