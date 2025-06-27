from django.urls import path
from client import views

urlpatterns = [
    
    path('overview/', views.overview, name='overview'),
    path('categories/', views.list_category, name='categories'),
    path('transactions/', views.list_transaction, name='transactions'),
    path('analytics/', views.analytics, name='analytics'),
    path('groups/', views.list_group, name='groups'),

    path('category-expense-analysis/', views.render_category_wise_expense, name='category-wise-expense'),
    path('transaction-analysis/', views.render_date_wise_transaction, name='date-wise-transaction'),

    path('login/', views.login_user, name='login_user'),

]

