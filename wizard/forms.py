from django import forms
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from group.models import Group, Expense
from finance.models import CustomUser


class GroupWidget(ModelSelect2Widget):
    model = Group
    search_fields = ["name__icontains"]
    

class SelectGroupForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=GroupWidget(),
        label="Select a Group"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['group'].queryset = Group.objects.all()
        # self.fields['group'].label_from_instance = lambda obj: obj.name
        print("Groups available:", self.fields['group'].queryset)


class ExpenseDetailsForm(forms.Form):
    description = forms.CharField(max_length=255)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)


class CustomUserWidget(ModelSelect2MultipleWidget):
    model = CustomUser
    search_fields = ['username__icontains', 'email__icontains']
    delay = 3000  # 3 seconds debounce delay
    attrs = {
        'data-minimum-input-length': 1,
        'data-delay': '3000',
    }

class SplitUsersForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=CustomUserWidget()
    )
