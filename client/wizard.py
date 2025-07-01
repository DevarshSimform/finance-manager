import requests
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from formtools.wizard.views import SessionWizardView

from .forms import EmailForm, UserRegistrationForm

logger = logging.getLogger(__name__)

class RegistrationWizard(SessionWizardView):
    form_list = [EmailForm, UserRegistrationForm]
    template_name = 'client/register_user_wizard/wizard_form.html'
    
    def get_template_names(self):
        # Return template for current step
        if self.steps.current == '0':
            return ['client/register_user_wizard/register_step1.html']
        elif self.steps.current == '1':
            return ['client/register_user_wizard/register_step2.html']
        return [self.template_name]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        
        # Add step info to context
        if self.steps.current == '0':
            context.update({'step_title': 'Step 1: Email Address'})
        elif self.steps.current == '1':
            context.update({'step_title': 'Step 2: Create Your Account'})
            
            # Get email from step 1 and add to context
            email = self.get_cleaned_data_for_step('0')['email']
            context.update({'email': email})
            
        return context

    def done(self, form_list, **kwargs):
        # Process the form data
        form_data = [form.cleaned_data for form in form_list]
        
        # Extract data from forms
        email = form_data[0]['email']
        username = form_data[1]['username']
        password = form_data[1]['password']
        
        # Prepare data for API request
        registration_data = {
            'email': email,
            'username': username,
            'password': password
        }
        
        try:
            # Send POST request to registration API
            response = requests.post(
                'http://127.0.0.1:8000/api/auth/register/',
                json=registration_data,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10  # Set a timeout for the request
            )
            
            # Check if the request was successful
            if response.status_code == 201 or response.status_code == 200:
                # Registration successful, display success message
                messages.success(
                    self.request,
                    'Your account has been created successfully! Please check your email to verify your account.'
                )
                # Redirect to the email verification page
                return redirect(reverse('register_check_email'))
            else:
                # Registration failed, display error message
                error_msg = 'Registration failed. '
                
                # Try to extract error message from response
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += error_data['message']
                    elif 'error' in error_data:
                        error_msg += error_data['error']
                    # Handle specific errors
                    elif 'email' in error_data:
                        error_msg += f"Email error: {error_data['email'][0]}"
                    elif 'username' in error_data:
                        error_msg += f"Username error: {error_data['username'][0]}"
                    elif 'password' in error_data:
                        error_msg += f"Password error: {error_data['password'][0]}"
                except ValueError:
                    error_msg += 'An unexpected error occurred.'
                
                messages.error(self.request, error_msg)
                # Redirect back to the beginning of the registration process
                return redirect(reverse('registration_wizard'))
                
        except requests.RequestException as e:
            # Handle request exceptions (network issues, timeouts, etc.)
            logger.error(f"API request error during registration: {str(e)}")
            messages.error(
                self.request,
                'Unable to connect to the registration service. Please try again later.'
            )
            return redirect(reverse('registration_wizard'))