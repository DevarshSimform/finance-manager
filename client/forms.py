from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div

from django import forms
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from group.models import Group

User = get_user_model()

class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'id': 'regEmail'
        }),
        label="Email Address"
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists. Please login.")
        return email

class UserRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'id': 'regUsername'
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'regPassword'
        }),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'regConfirmPassword'
        }),
        label="Confirm Password"
    )

    def clean_username(self):
        # Basic validation - proper API validation will happen when the form is submitted
        username = self.cleaned_data.get('username')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class CustomUserSelect2Widget(ModelSelect2MultipleWidget):
    model = User
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'username__icontains',
        'email__icontains',
    ]

class GroupCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).exclude(email='AnonymousUser').order_by('first_name', 'last_name'),
        widget=CustomUserSelect2Widget(
            attrs={
            'data-placeholder': 'Search users...',
            'data-minimum-input-length': 1,
            'data-delay': 300,
            'id': 'id_users',
        }
        )
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['members'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})"
        self.helper = FormHelper()
        self.helper.form_id = 'groupForm'
        self.helper.form_method = 'post'
        self.helper.form_tag = False  # form tag in template

        self.helper.layout = Layout(
            Field('name', css_class='mb-3'),
            Field('members', css_class='mb-3'),
        )