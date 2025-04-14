# urls.py
from django.urls import path
from authentication import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view()),
    path('logout/', views.LogoutAPIView.as_view()),
    path('register/', views.RegisterAPIView.as_view()),
    path('verify-email/', views.VerifyEmailAPIView.as_view(), name='verify-email'),
]
