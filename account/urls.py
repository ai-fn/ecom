from django.urls import path, include

from account import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.Register.as_view(), name='register'),
    path('verify-email/<uid64>/<token>/', views.EmailVerifyView.as_view(), name='verify-email'),
]