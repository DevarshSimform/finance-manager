from django.urls import path
from finance import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('transactions/', views.TransactionListCreateAPIView.as_view()),
    path('transactions/<uuid:pk>/', views.TransactionRetrieveUpdateDestroyAPIView.as_view()),
    path('balance/', views.BalanceViewAPIView.as_view()),

    path('category/', views.CategoryListAPIView.as_view()),
    path('category/add/', views.CategoryCreateAPIView.as_view()),
    path('category/<uuid:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view()),


]
