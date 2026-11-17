from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import models
from django.db.models import DecimalField, ProtectedError, Q, RestrictedError, Sum, Value
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from ebanking_app.form import *  # this will import all the forms that we created in the form.py file in the ebanking_app application


# ---------------------------------------------------------------------------
# AUTHENTICATION VIEWS
# here we use the authentication system that ships with Django (the auth_user table) instead of our own Login model, so passwords are stored as secure hashes and Django remembers who is logged in.
# ---------------------------------------------------------------------------

def login_view(request):
    # if the user is already logged in there is no need to show the login page again, so we send them to the dashboard
    if request.user.is_authenticated:
        return redirect('home_page')

    # this checks if the request method is POST, which means that the form has been submitted.
    if request.method == 'POST':
        # AuthenticationForm is Django's built-in login form. It checks that the username exists and that the password is correct.
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # login() saves the user in the session so that every page after this knows who is logged in
            login(request, form.get_user())
            messages.success(request, f'Welcome back, {form.get_user().username}!')
            # if the user was sent here from a protected page, Django adds ?next=/that-page/ to the URL. We send them back there after login, but only if it is a page on our own site.
            next_page = request.POST.get('next') or request.GET.get('next')
            if next_page and url_has_allowed_host_and_scheme(next_page, allowed_hosts={request.get_host()}):
                return redirect(next_page)
            return redirect('home_page')
    else:
        # else, if the request method is not POST (the user is opening the page for the first time), we show an empty login form
        form = AuthenticationForm(request)
    return render(request, 'registration/login.html', {'form': form, 'next': request.GET.get('next', '')})


def sign_up_view(request):
    if request.method == 'POST':
        # UserCreationForm is Django's built-in sign up form. It asks for a username and a password (typed twice) and checks the password rules in settings.py
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # save() creates the new row in the auth_user table, with the password stored as a hash
            user = form.save()
            # we log the new user in straight away so they do not have to type their details again
            login(request, user)
            messages.success(request, 'Your account was created successfully.')
            return redirect('home_page')
    else:
        form = UserCreationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


# @require_POST means this view only accepts a POST request (from the Logout button form). Django 5 requires logging out with POST so that another website cannot log our users out with a simple link.
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login_page')


# @login_required protects a view: a visitor who is not logged in is redirected to the login page (LOGIN_URL in settings.py) and brought back here after logging in
@login_required
def home_view(request):
    # here we count the numbers shown on the dashboard stat cards (Admin Dashboard lecture). Each line is one small query on the database.
    # count() is the ORM version of SELECT COUNT(*). aggregate(Sum(...)) is the ORM version of SELECT SUM(...) and returns a dictionary, e.g. {'total': Decimal('150000.00')}.
    # Coalesce() turns "no rows yet" (NULL) into 0 so the card shows 0.00 instead of nothing.
    total_balance = Accounts.objects.aggregate(
        total=Coalesce(Sum('account_balance'), Value(Decimal('0')), output_field=DecimalField())
    )['total']
    total_repaid = LoanPayment.objects.aggregate(
        total=Coalesce(Sum('paid_amount'), Value(Decimal('0')), output_field=DecimalField())
    )['total']

    context = {
        'customer_count': Customer.objects.count(),
        'account_count': Accounts.objects.count(),
        'total_balance': total_balance,
        'loan_count': Loans.objects.count(),
        # filter() is the ORM version of WHERE, so this counts only loans whose status is 'P' (Pending)
        'pending_loan_count': Loans.objects.filter(loan_status='P').count(),
        'payment_count': LoanPayment.objects.count(),
        'total_repaid': total_repaid,
    }
    return render(request, 'home.html', context)


# ---------------------------------------------------------------------------
# CRUD (Create, Read, Update, Delete) SETTINGS FOR EACH TABLE
# here we list every table that can be managed from the website. For each one we store:
#   form     - the form class from form.py used to add and edit records
#   template - the page with the "add" form
#   page     - the name of that page's URL (from urls.py)
#   label    - a friendly name for one record, used in messages
#   title    - the heading of the records page
#   columns  - (column heading, field name) pairs shown on the records and details pages. A dot follows a ForeignKey, e.g. 'loan_request.customer' means "the customer of this loan's request".
# the key (e.g. 'customer') is the same word used at the start of that page's URL, e.g. /customer/ and /customer/records/
# ---------------------------------------------------------------------------

RECORD_TYPES = {
    'bankstaff': {
        'form': BankstaffForm, 'template': 'bank_staff.html', 'page': 'bank_staff_page', 'label': 'Bank staff member', 'title': 'Bank Staff Records',
        'columns': [('Employee No', 'employee_number'), ('First Name', 'first_name'), ('Last Name', 'last_name'), ('Phone', 'phone_number'), ('Gender', 'gender'),
                    ('Marital Status', 'marital_status'), ('Dependants', 'number_of_dependants'), ('Department', 'department'), ('Position', 'position'),
                    ('Address', 'address'), ('Registered On', 'registration_date')],
    },
    'customer': {
        'form': CustomerForm, 'template': 'customer.html', 'page': 'customer_page', 'label': 'Customer', 'title': 'Customer Records',
        'columns': [('First Name', 'first_name'), ('Last Name', 'last_name'), ('Phone', 'phone_number'), ('Gender', 'gender'), ('Date of Birth', 'date_of_birth'),
                    ('Marital Status', 'marital_status'), ('Occupation', 'occupation'), ('Address', 'address'), ('Registered On', 'registration_date')],
    },
    'accounts': {
        'form': AccountsForm, 'template': 'accounts.html', 'page': 'accounts_page', 'label': 'Account', 'title': 'Bank Account Records',
        'columns': [('Account No', 'account_number'), ('Account Type', 'account_type'), ('Balance', 'account_balance'), ('Customer', 'customer'),
                    ('Opened On', 'account_open_date')],
    },
    'guarantor': {
        'form': GuarantorForm, 'template': 'guarantor.html', 'page': 'guarantor_page', 'label': 'Guarantor', 'title': 'Guarantor Records',
        'columns': [('First Name', 'first_name'), ('Last Name', 'last_name'), ('Phone', 'phone_number'), ('Gender', 'gender'), ('Date of Birth', 'date_of_birth'),
                    ('Occupation', 'occupation'), ('Address', 'address')],
    },
    'loanproduct': {
        'form': LoanProductsForm, 'template': 'loan_products.html', 'page': 'loan_product_page', 'label': 'Loan product', 'title': 'Loan Product Records',
        'columns': [('Product Code', 'product_code'), ('Product Name', 'product_name'), ('Min Amount', 'min_loan_amount'), ('Max Amount', 'max_loan_amount'),
                    ('Max Period (Weeks)', 'max_repayment_period_in_weeks'), ('Repayment Cycle', 'repayment_cycle')],
    },
    'loanrequest': {
        'form': LoanRequestsForms, 'template': 'loan_requests.html', 'page': 'loan_request_page', 'label': 'Loan request', 'title': 'Loan Request Records',
        'columns': [('Request Date', 'request_date'), ('Customer', 'customer'), ('Loan Product', 'loan_product'), ('Loan Amount', 'loan_amount'),
                    ('Period (Weeks)', 'repayment_period_in_weeks'), ('Repayment Cycle', 'repayment_cycle'), ('Guarantor', 'guarantor')],
    },
    'loans': {
        'form': LoansForm, 'template': 'loans.html', 'page': 'loan_view_page', 'label': 'Loan', 'title': 'Loan Records',
        'columns': [('Loan Request', 'loan_request'), ('Customer', 'loan_request.customer'), ('Loan Officer', 'loan_officer'),
                    ('Disbursement Date', 'loan_disbursement_date'), ('Status', 'loan_status')],
    },
    'loanapprovals': {
        'form': LoanApprovalsForm, 'template': 'loan_approvals.html', 'page': 'loan_approvals_page', 'label': 'Loan approval', 'title': 'Loan Approval Records',
        'columns': [('Loan', 'loan'), ('Approval Date', 'approval_date'), ('Approval Status', 'approval_status'), ('Bank Staff', 'bank_staff')],
    },
    'loanpayment': {
        'form': LoanPaymentForm, 'template': 'loan_payments.html', 'page': 'loan_payment_page', 'label': 'Loan payment', 'title': 'Loan Payment Records',
        'columns': [('Payment Ref Number', 'payment_reference_number'), ('Payment Date', 'payment_date'), ('Payment Method', 'payment_method'),
                    ('Paid Amount', 'paid_amount'), ('Paid By', 'paid_by'), ('Payment For', 'payment_for'), ('Processed By', 'processed_by')],
    },
    'transactiontypes': {
        'form': TransactionTypesForm, 'template': 'transaction_types.html', 'page': 'transaction_types_page', 'label': 'Transaction type', 'title': 'Transaction Type Records',
        'columns': [('Transaction Type', 'transaction_type'), ('Description', 'description')],
    },
    'transactions': {
        'form': TransactionsForm, 'template': 'transactions.html', 'page': 'transactions_page', 'label': 'Transaction', 'title': 'Transaction Records',
        'columns': [('Date & Time', 'transaction_date'), ('Transaction Type', 'transaction_type'), ('Amount', 'transaction_amount'), ('Account', 'account')],
    },
}


def get_record_type(record_type):
    # here we look up the settings for a table. If someone types a table name in the URL that does not exist, we show a "Page not found" (404) page.
    if record_type not in RECORD_TYPES:
        raise Http404('This type of record does not exist.')
    return RECORD_TYPES[record_type]


def display_value(record, field_path):
    # here we turn one field of a record into the text shown on the records and details pages
    value = record
    # 'loan_request.customer' is split into ['loan_request', 'customer'] and followed one step at a time
    for part in field_path.split('.'):
        if value is None:
            break
        # for fields with choices Django adds a get_<field>_display() method that returns the label (e.g. 'Male') instead of the stored value ('M')
        display_method = getattr(value, f'get_{part}_display', None)
        value = display_method() if callable(display_method) else getattr(value, part)

    if value is None or value == '':
        return '-'
    # datetime must be checked before date, because a datetime is also a date
    if isinstance(value, datetime):
        return timezone.localtime(value).strftime('%Y-%m-%d %H:%M')
    # money is shown with thousands separators and 2 decimal places, e.g. 1,500,000.00
    if isinstance(value, Decimal):
        return f'{value:,.2f}'
    return value


# ---------------------------------------------------------------------------
# C - Create
# every "add" page works the same way, so instead of repeating the same code 11 times (DRY - Don't Repeat Yourself) this helper does the work and each page's view calls it.
# ---------------------------------------------------------------------------

def create_record(request, record_type):
    # this shows the "add" form and saves a new record when the form is submitted
    settings = get_record_type(record_type)
    form_class = settings['form']

    if request.method == 'POST':
        form = form_class(request.POST)
        # is_valid() checks every field against the rules in models.py and form.py
        if form.is_valid():
            form.save()
            # messages lets us show a one-time notice on the next page that is opened
            messages.success(request, f"{settings['label']} saved successfully.")
            # after saving we go to the records page so the user can see the new record. Redirecting also stops the browser from saving the same record again if the user refreshes the page.
            return redirect('record_list_page', record_type=record_type)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = form_class()

    context = {
        'form': form,
        'record_type': record_type,
    }
    return render(request, settings['template'], context)


# ---------------------------------------------------------------------------
# PAGE VIEWS (Create)
# each "add" page has its own view so that its URL in urls.py stays the same. @login_required makes sure only logged in users can see or change records.
# ---------------------------------------------------------------------------

@login_required
def accounts_view(request):
    return create_record(request, 'accounts')

@login_required
def bankstaff_view(request):
    return create_record(request, 'bankstaff')

@login_required
def customer_view(request):
    return create_record(request, 'customer')

@login_required
def guarantor_view(request):
    return create_record(request, 'guarantor')

@login_required
def loanapprovals_view(request):
    return create_record(request, 'loanapprovals')

@login_required
def loanpayment_view(request):
    return create_record(request, 'loanpayment')

@login_required
def loanproduct_view(request):
    return create_record(request, 'loanproduct')

@login_required
def loanrequest_view(request):
    return create_record(request, 'loanrequest')

@login_required
def loan_view(request):
    return create_record(request, 'loans')

@login_required
def transactiontypes_view(request):
    return create_record(request, 'transactiontypes')

@login_required
def transactions_view(request):
    return create_record(request, 'transactions')


# ---------------------------------------------------------------------------
# R - Read
# one records page and one details page serve every table. The URL tells them which table (record_type) and, for details, which row (record_id), e.g. /customer/records/ and /customer/3/
# ---------------------------------------------------------------------------

@login_required
def record_list_view(request, record_type):
    # this page lists every saved record of one table, with a search box
    settings = get_record_type(record_type)
    model = settings['form']._meta.model

    # SELECT * FROM table  ->  Model.objects.all(). Newest records are shown first.
    records = model.objects.all().order_by('-id')

    # the search box is a Django form. Searching uses GET so the search words appear in the URL and the page can be refreshed or bookmarked.
    search_form = SearchForm(request.GET)
    search_text = ''
    if search_form.is_valid():
        search_text = search_form.cleaned_data['q']
    if search_text:
        # Q objects let us combine conditions with OR (|). We look for the search words in every text field of the table, e.g. WHERE first_name LIKE '%john%' OR last_name LIKE '%john%' ...
        condition = Q()
        for field in model._meta.fields:
            if isinstance(field, models.CharField):
                condition |= Q(**{f'{field.name}__icontains': search_text})
        # typing a number also finds the record with that ID
        if search_text.isdigit():
            condition |= Q(id=int(search_text))
        records = records.filter(condition)

    # here we prepare each table row: the record itself (for the View / Edit / Delete buttons) and the text of each column
    rows = []
    for record in records:
        rows.append({
            'record': record,
            'cells': [display_value(record, field_path) for heading, field_path in settings['columns']],
        })

    context = {
        'rows': rows,
        'headings': [heading for heading, field_path in settings['columns']],
        'record_type': record_type,
        'title': settings['title'],
        'label': settings['label'],
        'add_page': settings['page'],
        'search_form': search_form,
        'search_text': search_text,
    }
    return render(request, 'record_list.html', context)


@login_required
def record_detail_view(request, record_type, record_id):
    # this page shows every detail of ONE record
    settings = get_record_type(record_type)
    # SELECT * FROM table WHERE id=record_id  ->  get_object_or_404 shows a 404 page if the row does not exist, instead of crashing
    record = get_object_or_404(settings['form']._meta.model, id=record_id)

    # each detail is a (heading, value) pair shown as one row of the details table
    details = [(heading, display_value(record, field_path)) for heading, field_path in settings['columns']]

    context = {
        'record': record,
        'details': details,
        'record_type': record_type,
        'label': settings['label'],
        'title': settings['title'],
    }
    # when the View icon on the records page is clicked, popups.js asks for this page with ?popup=1 added to the address.
    # In that case we send back only the details (popup_detail.html, which does not extend base.html), and popups.js puts it inside the popup window.
    if request.GET.get('popup'):
        return render(request, 'popup_detail.html', context)
    return render(request, 'record_detail.html', context)


# ---------------------------------------------------------------------------
# U - Update and D - Delete
# one edit view and one delete view serve every table, e.g. /customer/3/edit/ and /customer/3/delete/
# ---------------------------------------------------------------------------

@login_required
def edit_record_view(request, record_type, record_id):
    settings = get_record_type(record_type)
    form_class = settings['form']
    record = get_object_or_404(form_class._meta.model, id=record_id)
    # popup is True when the form is opened (or saved) inside the popup window on the records page. popups.js adds ?popup=1 to the address.
    popup = bool(request.GET.get('popup'))

    if request.method == 'POST':
        # instance=record tells the ModelForm to UPDATE this existing row instead of INSERTING a new one
        form = form_class(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, f"{settings['label']} updated successfully.")
            if popup:
                # from the popup we answer with a redirect. popups.js sees it, closes the popup and reloads the page underneath, which then shows the success message.
                return redirect('record_list_page', record_type=record_type)
            # after saving we show the updated record's details
            return redirect('record_detail_page', record_type=record_type, record_id=record.id)
        # in the popup the errors are shown under each field, so we do not add a message (it would wait and appear on the next page instead)
        if not popup:
            messages.error(request, 'Please correct the errors below.')
    else:
        # on a normal visit (GET) we fill the form with the record's current values
        form = form_class(instance=record)

    context = {
        'form': form,
        'record': record,
        'record_type': record_type,
        'label': settings['label'],
    }
    # in the popup we send back only the form (popup_edit.html, which does not extend base.html)
    if popup:
        return render(request, 'popup_edit.html', context)
    return render(request, 'edit_record.html', context)


# deleting changes data, so it only accepts POST (from the Delete button form with its csrf_token), never a plain link
@login_required
@require_POST
def delete_record_view(request, record_type, record_id):
    settings = get_record_type(record_type)
    record = get_object_or_404(settings['form']._meta.model, id=record_id)
    try:
        record.delete()
        messages.success(request, f"{settings['label']} deleted successfully.")
    except (ProtectedError, RestrictedError):
        # our ForeignKeys use on_delete=models.RESTRICT, so Django refuses to delete a record that other records still point to (e.g. a customer who still has accounts). We show a message instead of crashing.
        messages.error(request, f"This {settings['label'].lower()} cannot be deleted because other records are linked to it. Delete or change those records first.")
        # the Delete icon on the records page sends a hidden field return_to=list, so the user stays on the records page and sees the message there
        if request.POST.get('return_to') == 'list':
            return redirect('record_list_page', record_type=record_type)
        return redirect('record_detail_page', record_type=record_type, record_id=record.id)
    return redirect('record_list_page', record_type=record_type)


# ---------------------------------------------------------------------------
# REPORTS
# ---------------------------------------------------------------------------

@login_required
def loanrepayments_view(request):
    # here we build a repayment summary for every loan: the amount borrowed, the total paid so far and what is still owed.
    # Sum() adds up all the payments linked to each loan (the loanpayment relation comes from LoanPayment.payment_for). Coalesce() turns "no payments yet" (NULL) into 0.
    loans = Loans.objects.select_related(
        'loan_request__customer', 'loan_request__loan_product'
    ).annotate(
        total_paid=Coalesce(Sum('loanpayment__paid_amount'), Value(Decimal('0')), output_field=DecimalField())
    ).order_by('-id')

    # the remaining balance is the loan amount minus what has been paid
    for loan in loans:
        loan.remaining_balance = loan.loan_request.loan_amount - loan.total_paid

    return render(request, 'loan_repayment_summary.html', {'loans': loans})
