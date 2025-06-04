# from django.urls import path, include

# urlpatterns = [
#     # other paths...
#     path('select2/', include('django_select2.urls')),
# ]

from django.urls import path
from wizard.views import ExpenseWizard, select_group_view, FORMS
from wizard.forms import SelectGroupForm, ExpenseDetailsForm, SplitUsersForm

urlpatterns = [
    path('ewizard/', ExpenseWizard.as_view(), name='expense_wizard'),
    path('noname/', select_group_view),
]
