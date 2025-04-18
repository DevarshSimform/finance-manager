from django.urls import path
from developersOnly import views

urlpatterns = [
    
    path('transactions/all', views.AllTransactionAPIView.as_view(), name='transaction-all'),
    path('transactions/deleted', views.DeletedTransactionAPIView.as_view(), name='transaction-deleted'),
    path('transactions/restore/<uuid:pk>', views.RestoreTransactionAPIView.as_view(), name='transaction-restore'),
    path('transactions/hard-delete/<uuid:pk>', views.HardDeleteTransactionAPIView.as_view(), name='transaction-hard-delete'),


    path('users/all', views.AllUserAPIView.as_view(), name='user-all'),
    path('users/deleted', views.DeletedUserAPIView.as_view(), name='user-deleted'),
    path('users/restore/<int:pk>', views.RestoreUserAPIView.as_view(), name='user-restore'),


]
