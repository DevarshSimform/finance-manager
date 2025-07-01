from django.urls import path
from client import views
from client.wizard import RegistrationWizard
from client.forms import EmailForm, UserRegistrationForm

# Registration wizard forms
registration_forms = [EmailForm, UserRegistrationForm]

urlpatterns = [
    
    path('', views.overview, name='overview'),
    path('overview/', views.overview, name='overview'),
    path('categories/', views.list_category, name='categories'),
    path('transactions/', views.list_transaction, name='transactions'),
    path('analytics/', views.analytics, name='analytics'),
    path('groups/', views.list_group, name='groups'),
    path('group/create/', views.group_create_view, name='group_create'),
    path('groups/<int:group_id>/', views.get_group_detail, name='group_detail'),

    path('category-expense-analysis/', views.render_category_wise_expense, name='category-wise-expense'),
    path('transaction-analysis/', views.render_date_wise_transaction, name='date-wise-transaction'),

    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),

    # Registration wizard URLs
    path('register/wizard/', RegistrationWizard.as_view(form_list=registration_forms), name='registration_wizard'),

    # Keep the original URLs for backward compatibility
    path('register/step1/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('register/check-email/', views.register_check_email, name='register_check_email'),
    
]

