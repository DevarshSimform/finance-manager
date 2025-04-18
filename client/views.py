from django.shortcuts import render


def home_page(request):
    return render(request, 'client/home.html')


def render_category_wise_expense(request):
    return render(request, 'client/category_wise_expense.html')


def render_date_wise_transaction(request):
    return render(request, 'client/date_wise_expense.html')


def login_user(request):
    return render(request, 'client/login.html')
    

def list_transaction(request):
    return render(request, 'client/list_transactions.html')


def list_category(request):
    return render(request, 'client/list_categories.html')

def transaction_log(request):
    return render(request, 'client/transaction_log.html')