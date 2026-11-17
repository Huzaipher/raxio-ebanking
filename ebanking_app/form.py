from django import forms
from django.forms import ModelForm
from .models import *

# here we create reusable widgets that tell the browser to show a date picker / date-and-time picker instead of a plain text box. Django's default DateInput is a plain text box, so we change its input_type.
class DateInput(forms.DateInput):
    input_type = 'date'

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

    # the browser's datetime-local box only understands the format YYYY-MM-DDTHH:MM, so we use that format when showing an existing value on the edit page
    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%dT%H:%M')
        super().__init__(**kwargs)


# here we create a plain Django form (not a ModelForm, because it does not save anything) for the search box on every records page
class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=100,
        label='Search',
        # attrs adds extra HTML attributes to the input box, here a hint shown inside the empty box
        widget=forms.TextInput(attrs={'placeholder': 'Type a name, number, code...'}),
    )


# UNUSED: logging in now uses Django's built-in AuthenticationForm (see views.py) and the Login model is commented out in models.py, so this form is commented out too.
# here create a new form class for the Login model by inheriting from ModelForm. The Meta class specifies the model to be used and the fields to be included in the form. In this case, all fields of the Login model are included in the form.
# class LoginForm(ModelForm):
#     class Meta:
#         model = Login
#         fields = '__all__'

class BankstaffForm(ModelForm):
    class Meta:
        model = Bankstaff
        fields = '__all__'
        # this widget tells the browser to show a date picker instead of a plain text box for the registration_date field 
        widgets = {'registration_date': DateInput()}

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'registration_date': DateInput(),
            'date_of_birth': DateInput(),
        }

class AccountsForm(ModelForm):
    class Meta:
        model = Accounts
        fields = '__all__'
        widgets = {'account_open_date': DateInput()}

class GuarantorForm(ModelForm):
    class Meta:
        model = Guarantor
        fields = '__all__'
        widgets = {'date_of_birth': DateInput()}

class LoanProductsForm(ModelForm):
    class Meta:
        model = LoanProducts
        fields = '__all__'

    # here the clean() method adds our own validation on top of what the model already checks. It runs when we call form.is_valid() in the view.
    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get('min_loan_amount')
        max_amount = cleaned_data.get('max_loan_amount')
        # a product cannot have a minimum loan amount that is bigger than its maximum loan amount
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise forms.ValidationError('The minimum loan amount cannot be greater than the maximum loan amount.')
        return cleaned_data

class LoanRequestsForms(ModelForm):
    class Meta:
        model = LoanRequests
        fields = '__all__'
        widgets = {'request_date': DateInput()}

    # here we check the request against the rules of the loan product that was chosen
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('loan_product')
        amount = cleaned_data.get('loan_amount')
        weeks = cleaned_data.get('repayment_period_in_weeks')
        if product and amount is not None:
            # add_error() attaches the message to one field so it shows right under that field on the page
            if amount < product.min_loan_amount or amount > product.max_loan_amount:
                self.add_error('loan_amount', f'{product.product_name} loans must be between {product.min_loan_amount} and {product.max_loan_amount}.')
        if product and weeks is not None and weeks > product.max_repayment_period_in_weeks:
            self.add_error('repayment_period_in_weeks', f'{product.product_name} loans must be repaid within {product.max_repayment_period_in_weeks} weeks.')
        return cleaned_data

class LoansForm(ModelForm):
    class Meta:
        model = Loans
        fields = "__all__"
        widgets = {'loan_disbursement_date': DateInput()}

class LoanApprovalsForm(ModelForm):
    class Meta:
        model = LoanApprovals
        fields = '__all__'
        widgets = {'approval_date': DateInput()}

class TransactionTypesForm(ModelForm):
    class Meta:
        model = TransactionTypes
        fields = '__all__'

# transaction_date is not shown in this form because the model fills it in automatically (auto_now_add=True)
class TransactionsForm(ModelForm):
    class Meta:
        model = Transactions
        fields = '__all__'

class LoanPaymentForm(ModelForm):
    class Meta:
        model = LoanPayment
        fields = '__all__'
        widgets = {'payment_date': DateTimeInput()}
