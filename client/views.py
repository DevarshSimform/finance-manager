from django.shortcuts import render, redirect



def overview(request):
    return render(request, 'client/overview.html')

def render_category_wise_expense(request):
    return render(request, 'client/category_wise_expense.html')

def render_date_wise_transaction(request):
    return render(request, 'client/date_wise_expense.html')

def analytics(request):
    return render(request, 'client/analytics.html')

def list_group(request):
    return render(request, 'client/groups.html')

def login_user(request):
    return render(request, 'client/login.html')

def list_transaction(request):
    return render(request, 'client/transactions.html')

def list_category(request):
    return render(request, 'client/categories.html')