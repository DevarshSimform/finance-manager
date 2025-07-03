from django.shortcuts import render
from client.forms import GroupCreateForm, ExpenseCreateForm


def overview(request):
    return render(request, 'client/overview.html')

def render_category_wise_expense(request):
    return render(request, 'client/category_wise_expense.html')

def render_date_wise_transaction(request):
    return render(request, 'client/date_wise_expense.html')

def analytics(request):
    return render(request, 'client/analytics.html')

def login_user(request):
    return render(request, 'client/login.html')

def register_user(request):
    """Main registration page that redirects to the first step"""
    return render(request, 'client/register_user_wizard/register.html')

def register_step1(request):
    """First step of registration - Email input with uniqueness validation"""
    return render(request, 'client/register_user_wizard/register_step1.html')

def register_step2(request):
    """Second step of registration - Username and password fields"""
    return render(request, 'client/register_user_wizard/register_step2.html')

def register_check_email(request):
    """Final step - Email verification confirmation page"""
    return render(request, 'client/register_user_wizard/register_check_email.html')

def list_group(request):
    return render(request, 'client/groups.html')

def group_create_view(request):
    form = GroupCreateForm()
    return render(request, 'client/group_create.html', {'form': form})

def expense_create_view(request):
    # form = ExpenseCreateForm()
    return render(request, 'client/expense_create.html')

def list_transaction(request):
    return render(request, 'client/transactions.html')

def list_category(request):
    return render(request, 'client/categories.html')

def get_group_detail(request, group_id):
    return render(request, 'client/group_detail.html', {'id': group_id})