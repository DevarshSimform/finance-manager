from django.urls import path
from finance import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('transactions/', views.TransactionListCreateAPIView.as_view(), name='transaction'),
    path('transactions/<uuid:pk>/', views.TransactionRetrieveUpdateDestroyAPIView.as_view(), name='transaction-single'),
    path('balance/', views.BalanceViewAPIView.as_view(), name='balance'),

    path('category/', views.CategoryListCreateAPIView.as_view(), name='category'),
    path('category/<uuid:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-single'),

    path('profile/', views.UserProfileView.as_view(), name='profile'),

    path('forgot-password/', views.RequestPasswordReset.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', views.ResetPassword.as_view(), name='reset-password'),

    path('category-wise-expanse/', views.GetCategoryTotal.as_view(), name='get_category_totals'),
    path('transaction-detail/', views.TransactionDetailByDate.as_view(), name='transaction_detials')
]
