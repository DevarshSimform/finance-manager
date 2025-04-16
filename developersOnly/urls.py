from django.urls import path
from developersOnly import views

urlpatterns = [
    
    path('transactions/all', views.AllTransactionAPIView.as_view()),
    path('transactions/deleted', views.DeletedTransactionAPIView.as_view()),
    path('transactions/restore/<uuid:pk>', views.RestoreTransactionAPIView.as_view()),
    path('transactions/hard-delete/<uuid:pk>', views.HardDeleteTransactionAPIView.as_view()),


    path('users/all', views.AllUserAPIView.as_view()),
    path('users/deleted', views.DeletedUserAPIView.as_view()),
    path('users/restore/<int:pk>', views.RestoreUserAPIView.as_view()),


]
