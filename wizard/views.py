from formtools.wizard.views import SessionWizardView
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from wizard.forms import SelectGroupForm, ExpenseDetailsForm, SplitUsersForm
from group.models import Expense, SplitExpense, Group



FORMS = [
    ("group", SelectGroupForm),
    ("details", ExpenseDetailsForm),
    ("split", SplitUsersForm),
]


TEMPLATES = {
    "group": "expense_wizard_group.html",
    "details": "expense_wizard_details.html",
    "split": "expense_wizard_split.html",
}

# @method_decorator(login_required, name='dispatch')
class ExpenseWizard(SessionWizardView):
    form_list = FORMS
    # form_list = [SelectGroupForm, ExpenseDetailsForm, SplitUsersForm]

    def post(self, *args, **kwargs):
        request = self.request

        if 'save' in request.POST:
            form = self.get_form(data=request.POST, files=request.FILES)
            if form.is_valid():
                # Save current step data and files to storage
                self.storage.set_step_data(self.steps.current, self.process_step(form))
                self.storage.set_step_files(self.steps.current, self.process_step_files(form))

                # Now reload the form with saved data from storage so data is displayed
                # get the data dict saved in storage for current step
                step_data = self.storage.get_step_data(self.steps.current)
                step_files = self.storage.get_step_files(self.steps.current)

                # Construct a form instance initialized with stored data/files
                form = self.get_form(data=step_data, files=step_files)

                # Render the form with the saved data visible
                return self.render(form)

            else:
                # Invalid form, show errors
                return self.render(form)

        return super().post(*args, **kwargs)

    def get_template_names(self):
        # for step, form in FORMS:
        #     print(f"{step}: {form} ({type(form)})")
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        group = form_data[0]['group']
        description = form_data[1]['description']
        amount = form_data[1]['amount']
        users = form_data[2]['users']

        expense = Expense.objects.create(
            group=group,
            created_by=self.request.user,
            description=description,
            amount=amount,
        )

        split_amount = round(amount / users.count(), 2)

        for user in users:
            SplitExpense.objects.create(
                expense=expense,
                user=user,
                amount=split_amount
            )

        return render(self.request, "expense_done.html", {'expense': expense})


def select_group_view(request):
    form = SelectGroupForm(request.POST or None)
    if form.is_valid():
        group = form.cleaned_data['group']
        print(group)
        # Do something with selected group
    return render(request, 'expense_wizard.html', {'form': form})
