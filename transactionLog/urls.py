from django.urls import path
from transactionLog.views import TransactionLogListAPIView

urlpatterns = [
    path('', TransactionLogListAPIView.as_view(), name='transactionlog-list'),
    
]
