from django.urls import path
from finance import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('transactions/', views.TransactionListCreateAPIView.as_view()),
    path('transactions/<uuid:pk>/', views.TransactionRetrieveUpdateDestroyAPIView.as_view()),
    path('balance/', views.BalanceViewAPIView.as_view()),

    path('category/', views.CategoryListCreateAPIView.as_view()),
    path('category/<uuid:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view()),

    path('profile/', views.UserProfileView.as_view()),

    path('forgot-password/', views.RequestPasswordReset.as_view()),
    path('reset-password/<str:token>/', views.ResetPassowrd.as_view()),

    path('total/', views.GetCategoryTotal.as_view(), name='get_category_totals'),
    path('transaction-detail/', views.TransactionDetailByDate.as_view(), name='transaction_detials')
]
