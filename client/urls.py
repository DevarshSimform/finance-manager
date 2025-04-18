from django.urls import path
from client.views import (
    render_category_wise_expense, 
    render_date_wise_transaction, 
    home_page, 
    login_user, 
    list_transaction, 
    list_category,
    transaction_log
)

urlpatterns = [
    path('home/', home_page, name='home'),

    path('category-expense-analysis/', render_category_wise_expense, name='category-wise-expense'),
    path('transaction-analysis/', render_date_wise_transaction, name='date-wise-transaction'),

    path('login/', login_user, name='login'),

    path('transaction/', list_transaction, name='transaction'),
    path('category/', list_category, name='category'),

    path('log/', transaction_log, name='log')

]

