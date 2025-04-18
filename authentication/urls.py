# urls.py
from django.urls import path
from authentication import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailAPIView.as_view(), name='verify-email'),
]
