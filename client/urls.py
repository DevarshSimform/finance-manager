from django.urls import path
from client.views import render_category_wise_expense, render_date_wise_transaction

urlpatterns = [
    path('category/', render_category_wise_expense, name='category'),
    path('date/', render_date_wise_transaction, name='date'),
]

