from django.urls import path
from finance import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('login/', views.LoginAPIView.as_view()),
    path('logout/', views.LogoutAPIView.as_view()),
    path('register/', views.RegisterAPIView.as_view()),

    path('transactions/', views.TransactionListCreateApiView.as_view()),
    path('transactions/<uuid:pk>/', views.TransactionRetrieveUpdateDestroyApiView.as_view()),
    path('balance/', views.BalanceViewAPIView.as_view()),


    # for devloper use
    path('transactions/all/', views.AllTransactionAPIView.as_view()),
    path('transactions/deleted/', views.DeletedTransactionAPIView.as_view()),
    path('transactions/restore/<uuid:pk>/', views.RestoreTransactionAPIView.as_view()),
    path('transactions/hard-delete/<uuid:pk>/', views.HardDeleteTransactionAPIView.as_view()),

]
