from django.shortcuts import render


def render_category_wise_expense(request):
    return render(request, 'client/category_wise_expense.html')

def render_date_wise_transaction(request):
    return render(request, 'client/date_wise_expense.html')
