from django.urls import path
from finance import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('transactions/', views.TransactionListCreateApiView.as_view()),
    path('transactions/<uuid:pk>/', views.TransactionRetrieveUpdateDestroyApiView.as_view()),
]
