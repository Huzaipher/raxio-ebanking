from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import *

# Create your tests here.
# run them with:  python manage.py test ebanking_app
# Django creates a separate, empty test database for these tests, so your real db.sqlite3 data is never touched.


class AuthenticationTests(TestCase):
    # here we test signing up, logging in, logging out and protected pages

    def setUp(self):
        # setUp runs before every test and creates a user we can log in with
        self.user = User.objects.create_user(username='teller', password='Str0ng-Pass-123')

    def test_login_page_loads_with_logo(self):
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/static/images/e_banking_logo.jpeg')

    def test_logo_file_is_found(self):
        # the image must actually be found by Django's static files system (the same system runserver uses to serve /static/ files)
        from django.contrib.staticfiles import finders
        self.assertIsNotNone(finders.find('images/e_banking_logo.jpeg'))

    def test_protected_page_redirects_to_login(self):
        response = self.client.get(reverse('customer_page'))
        self.assertRedirects(response, reverse('login_page') + '?next=' + reverse('customer_page'))

    def test_login_with_correct_password(self):
        response = self.client.post(reverse('login_page'), {'username': 'teller', 'password': 'Str0ng-Pass-123'})
        self.assertRedirects(response, reverse('home_page'))
        # the home page now opens because the user is logged in
        self.assertEqual(self.client.get(reverse('home_page')).status_code, 200)

    def test_login_returns_to_next_page(self):
        response = self.client.post(reverse('login_page'), {'username': 'teller', 'password': 'Str0ng-Pass-123', 'next': reverse('accounts_page')})
        self.assertRedirects(response, reverse('accounts_page'))

    def test_login_ignores_next_page_on_another_website(self):
        response = self.client.post(reverse('login_page'), {'username': 'teller', 'password': 'Str0ng-Pass-123', 'next': 'https://evil.example.com/'})
        self.assertRedirects(response, reverse('home_page'))

    def test_login_with_wrong_password_shows_error(self):
        response = self.client.post(reverse('login_page'), {'username': 'teller', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_sign_up_creates_user_and_logs_in(self):
        response = self.client.post(reverse('sign_up_page'), {'username': 'newstaff', 'password1': 'Another-Pass-456', 'password2': 'Another-Pass-456'})
        self.assertRedirects(response, reverse('home_page'))
        self.assertTrue(User.objects.filter(username='newstaff').exists())
        # the password is stored as a hash, never as the typed text
        self.assertNotEqual(User.objects.get(username='newstaff').password, 'Another-Pass-456')

    def test_sign_up_with_mismatched_passwords_fails(self):
        response = self.client.post(reverse('sign_up_page'), {'username': 'newstaff', 'password1': 'Another-Pass-456', 'password2': 'different-456'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newstaff').exists())

    def test_logout(self):
        self.client.login(username='teller', password='Str0ng-Pass-123')
        # logging out with a plain link (GET) is not allowed
        self.assertEqual(self.client.get(reverse('logout_page')).status_code, 405)
        response = self.client.post(reverse('logout_page'))
        self.assertRedirects(response, reverse('login_page'))
        # after logging out the protected pages redirect to login again
        self.assertEqual(self.client.get(reverse('home_page')).status_code, 302)


class CrudTests(TestCase):
    # here we test Create, Read, Update and Delete on every page

    def setUp(self):
        self.user = User.objects.create_user(username='teller', password='Str0ng-Pass-123')
        self.client.login(username='teller', password='Str0ng-Pass-123')

        # one saved record of each table, so that ForeignKey dropdowns have something to choose from
        self.staff = Bankstaff.objects.create(first_name='Sarah', last_name='Apio', registration_date=date(2024, 1, 10), employee_number='EMP0001',
                                              phone_number='0700000001', gender='F', marital_status='S', address='Kampala',
                                              number_of_dependants=0, department='Loans', position='Officer')
        self.customer = Customer.objects.create(first_name='John', last_name='Kato', registration_date=date(2024, 2, 1), phone_number='0700000002',
                                                gender='M', date_of_birth=date(1990, 5, 5), marital_status='M',
                                                address='Mbale', occupation='Teacher')
        self.account = Accounts.objects.create(account_number='ACC0000001', account_type='S', account_balance=Decimal('50000'),
                                               customer=self.customer, account_open_date=date(2024, 2, 2))
        self.guarantor = Guarantor.objects.create(first_name='Deo', last_name='Mutaasa', phone_number='0700000003', gender='M',
                                                  date_of_birth=date(1980, 1, 1), occupation='Farmer')
        self.product = LoanProducts.objects.create(product_code='BL01', product_name='Business Loan', max_loan_amount=Decimal('5000000'),
                                                   min_loan_amount=Decimal('100000'), max_repayment_period_in_weeks=52, repayment_cycle='M')
        self.request_obj = LoanRequests.objects.create(request_date=date(2024, 3, 1), loan_product=self.product, loan_amount=Decimal('1000000'),
                                                       repayment_period_in_weeks=24, repayment_cycle='M', customer=self.customer, guarantor=self.guarantor)
        self.loan = Loans.objects.create(loan_request=self.request_obj, loan_officer=self.staff, loan_disbursement_date=date(2024, 3, 5), loan_status='A')
        self.approval = LoanApprovals.objects.create(loan=self.loan, approval_date=date(2024, 3, 4), approval_status='A', bank_staff=self.staff)
        self.ttype = TransactionTypes.objects.create(transaction_type='Deposit', description='Money paid into an account')
        self.transaction = Transactions.objects.create(transaction_type=self.ttype, transaction_amount=Decimal('20000'), account=self.account)
        self.payment = LoanPayment.objects.create(payment_reference_number='REF-0001', payment_date=timezone.make_aware(datetime(2024, 4, 1, 10, 0)),
                                                  payment_method='MM', paid_amount=Decimal('300000'), paid_by=self.customer,
                                                  payment_for=self.loan, processed_by=self.staff)

    def cases(self):
        # for every page: (record type in the URL, page URL name, model, valid form data for a NEW record, a field + new value to test editing, the existing record to edit/delete)
        return [
            ('bankstaff', 'bank_staff_page', Bankstaff,
             {'first_name': 'Paul', 'last_name': 'Okello', 'registration_date': '2024-05-01', 'employee_number': 'EMP0002', 'phone_number': '0700000010',
              'gender': 'M', 'marital_status': 'M', 'address': 'Gulu', 'number_of_dependants': 2, 'department': 'Finance', 'position': 'Teller'},
             ('position', 'Manager'), lambda: self.staff),
            ('customer', 'customer_page', Customer,
             {'first_name': 'Mary', 'last_name': 'Nabiryo', 'registration_date': '2024-05-01', 'phone_number': '0700000011', 'gender': 'F',
              'date_of_birth': '1995-07-07', 'marital_status': 'S', 'address': 'Jinja', 'occupation': 'Nurse'},
             ('occupation', 'Doctor'), lambda: self.customer),
            ('accounts', 'accounts_page', Accounts,
             {'account_number': 'ACC0000002', 'account_type': 'C', 'account_balance': '1000.50', 'customer': self.customer.id, 'account_open_date': '2024-05-02'},
             ('account_type', 'FD'), lambda: self.account),
            ('guarantor', 'guarantor_page', Guarantor,
             {'first_name': 'Ann', 'last_name': 'Kisaakye', 'phone_number': '0700000012', 'gender': 'F', 'date_of_birth': '1985-03-03', 'address': '', 'occupation': 'Trader'},
             ('occupation', 'Banker'), lambda: self.guarantor),
            ('loanproduct', 'loan_product_page', LoanProducts,
             {'product_code': 'SL01', 'product_name': 'Salary Loan', 'max_loan_amount': '2000000', 'min_loan_amount': '50000',
              'max_repayment_period_in_weeks': 26, 'repayment_cycle': 'W'},
             ('product_name', 'Business Plus'), lambda: self.product),
            ('loanrequest', 'loan_request_page', LoanRequests,
             {'request_date': '2024-05-03', 'loan_product': self.product.id, 'loan_amount': '500000', 'repayment_period_in_weeks': 12,
              'repayment_cycle': 'W', 'customer': self.customer.id, 'guarantor': self.guarantor.id},
             ('repayment_cycle', 'Q'), lambda: self.request_obj),
            ('loans', 'loan_view_page', Loans,
             {'loan_request': self.request_obj.id, 'loan_officer': self.staff.id, 'loan_disbursement_date': '2024-05-04', 'loan_status': 'P'},
             ('loan_status', 'R'), lambda: self.loan),
            ('loanapprovals', 'loan_approvals_page', LoanApprovals,
             {'loan': self.loan.id, 'approval_date': '2024-05-05', 'approval_status': 'P', 'bank_staff': self.staff.id},
             ('approval_status', 'R'), lambda: self.approval),
            ('loanpayment', 'loan_payment_page', LoanPayment,
             {'payment_reference_number': 'REF-0002', 'payment_date': '2024-05-06T09:30', 'payment_method': 'BT', 'paid_amount': '150000',
              'paid_by': self.customer.id, 'payment_for': self.loan.id, 'processed_by': self.staff.id},
             ('payment_method', 'C'), lambda: self.payment),
            ('transactiontypes', 'transaction_types_page', TransactionTypes,
             {'transaction_type': 'Withdrawal', 'description': 'Money taken out of an account'},
             ('description', 'Cash withdrawal'), lambda: self.ttype),
            ('transactions', 'transactions_page', Transactions,
             {'transaction_type': self.ttype.id, 'transaction_amount': '7500', 'account': self.account.id},
             ('transaction_amount', '9999.00'), lambda: self.transaction),
        ]

    def edit_data(self, record_type, record):
        # the edit form needs every field, so we start from the record's current values (exactly what the edit page shows) and change one
        from .views import RECORD_TYPES
        form = RECORD_TYPES[record_type]['form'](instance=record)
        data = {}
        for name, field in form.fields.items():
            value = form.initial.get(name)
            if hasattr(value, 'strftime'):
                value = value.strftime('%Y-%m-%dT%H:%M') if isinstance(value, datetime) else value.strftime('%Y-%m-%d')
            data[name] = '' if value is None else value
        return data

    def test_create(self):
        for record_type, page, model, data, _, _ in self.cases():
            with self.subTest(page=page):
                before = model.objects.count()
                response = self.client.post(reverse(page), data)
                # a successful save redirects to the records page of that table
                self.assertRedirects(response, reverse('record_list_page', args=[record_type]), msg_prefix=str(getattr(response, 'context', None) and response.context.get('form').errors))
                self.assertEqual(model.objects.count(), before + 1)

    def test_create_with_missing_fields_shows_errors(self):
        for record_type, page, model, _, _, _ in self.cases():
            with self.subTest(page=page):
                before = model.objects.count()
                response = self.client.post(reverse(page), {})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'This field is required')
                self.assertEqual(model.objects.count(), before)

    def test_add_pages_have_no_table(self):
        # the "add" pages only show the form and a link to the records page
        for record_type, page, model, _, _, _ in self.cases():
            with self.subTest(page=page):
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, '<table')
                self.assertContains(response, reverse('record_list_page', args=[record_type]))

    def test_records_page(self):
        for record_type, page, model, _, _, get_record in self.cases():
            with self.subTest(page=page):
                response = self.client.get(reverse('record_list_page', args=[record_type]))
                self.assertEqual(response.status_code, 200)
                # the existing record is listed, with its View, Edit and Delete links
                self.assertIn(get_record(), [row['record'] for row in response.context['rows']])
                self.assertContains(response, reverse('record_detail_page', args=[record_type, get_record().id]))
                self.assertContains(response, reverse('edit_record_page', args=[record_type, get_record().id]))
                self.assertContains(response, reverse('delete_record_page', args=[record_type, get_record().id]))

    def test_details_page(self):
        for record_type, page, model, _, _, get_record in self.cases():
            with self.subTest(page=page):
                response = self.client.get(reverse('record_detail_page', args=[record_type, get_record().id]))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['record'], get_record())
                self.assertContains(response, reverse('edit_record_page', args=[record_type, get_record().id]))

    def test_details_page_shows_labels_not_codes(self):
        response = self.client.get(reverse('record_detail_page', args=['customer', self.customer.id]))
        # gender 'M' and marital status 'M' are shown with their labels
        self.assertContains(response, 'Male')
        self.assertContains(response, 'Married')
        response = self.client.get(reverse('record_detail_page', args=['accounts', self.account.id]))
        # money is shown with thousands separators
        self.assertContains(response, '50,000.00')

    def test_search(self):
        Customer.objects.create(first_name='Mary', last_name='Nabiryo', registration_date=date(2024, 2, 1), phone_number='0700000099', gender='F',
                                date_of_birth=date(1995, 1, 1), marital_status='S', address='Jinja', occupation='Nurse')
        url = reverse('record_list_page', args=['customer'])
        # searching part of a name finds only the matching customer
        found = [row['record'].first_name for row in self.client.get(url, {'q': 'nabi'}).context['rows']]
        self.assertEqual(found, ['Mary'])
        # searching an ID finds that record
        found = [row['record'] for row in self.client.get(url, {'q': str(self.customer.id)}).context['rows']]
        self.assertIn(self.customer, found)
        # a search with no match shows the "no records" message
        self.assertContains(self.client.get(url, {'q': 'zzzz'}), 'No records match your search')
        # an empty search shows everything
        self.assertEqual(len(self.client.get(url, {'q': ''}).context['rows']), 2)

    def test_update(self):
        for record_type, page, model, _, (field, new_value), get_record in self.cases():
            with self.subTest(page=page):
                record = get_record()
                url = reverse('edit_record_page', args=[record_type, record.id])
                # the edit page opens with the form filled in
                self.assertEqual(self.client.get(url).status_code, 200)
                data = self.edit_data(record_type, record)
                data[field] = new_value
                response = self.client.post(url, data)
                # after saving, the user is shown the updated record's details
                self.assertRedirects(response, reverse('record_detail_page', args=[record_type, record.id]), msg_prefix=str(getattr(response, 'context', None) and response.context.get('form').errors))
                record.refresh_from_db()
                self.assertEqual(str(getattr(record, field)), str(new_value))
                # editing must not create a second record
                self.assertTrue(model.objects.filter(id=record.id).exists())

    def test_delete(self):
        # delete records in an order where nothing else points to them any more (children first)
        order = ['loanpayment', 'loanapprovals', 'transactions', 'transactiontypes', 'loans', 'loanrequest',
                 'loanproduct', 'guarantor', 'accounts', 'customer', 'bankstaff']
        cases = {c[0]: c for c in self.cases()}
        for record_type in order:
            _, page, model, _, _, get_record = cases[record_type]
            with self.subTest(page=page):
                record = get_record()
                url = reverse('delete_record_page', args=[record_type, record.id])
                # deleting with a plain link (GET) is not allowed
                self.assertEqual(self.client.get(url).status_code, 405)
                response = self.client.post(url)
                self.assertRedirects(response, reverse('record_list_page', args=[record_type]))
                self.assertFalse(model.objects.filter(id=record.id).exists())

    def test_delete_linked_record_is_refused(self):
        # the customer still has an account, loan request and payment, so on_delete=RESTRICT must stop the delete without crashing
        url = reverse('delete_record_page', args=['customer', self.customer.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot be deleted because other records are linked to it')
        self.assertTrue(Customer.objects.filter(id=self.customer.id).exists())

    def test_unknown_record_type_or_id_gives_404(self):
        self.assertEqual(self.client.get(reverse('edit_record_page', args=['nothing', 1])).status_code, 404)
        self.assertEqual(self.client.get(reverse('edit_record_page', args=['customer', 99999])).status_code, 404)
        self.assertEqual(self.client.get(reverse('record_list_page', args=['nothing'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('record_detail_page', args=['customer', 99999])).status_code, 404)

    def test_crud_pages_require_login(self):
        self.client.logout()
        for record_type, page, model, _, _, get_record in self.cases():
            with self.subTest(page=page):
                self.assertEqual(self.client.get(reverse(page)).status_code, 302)
                self.assertEqual(self.client.get(reverse('record_list_page', args=[record_type])).status_code, 302)
                self.assertEqual(self.client.get(reverse('record_detail_page', args=[record_type, get_record().id])).status_code, 302)
                self.assertEqual(self.client.post(reverse('delete_record_page', args=[record_type, get_record().id])).status_code, 302)
                self.assertTrue(model.objects.filter(id=get_record().id).exists())


class FormRuleTests(TestCase):
    # here we test the extra validation rules we wrote in form.py

    def setUp(self):
        User.objects.create_user(username='teller', password='Str0ng-Pass-123')
        self.client.login(username='teller', password='Str0ng-Pass-123')

    def test_loan_product_min_cannot_exceed_max(self):
        response = self.client.post(reverse('loan_product_page'), {'product_code': 'X1', 'product_name': 'Bad', 'max_loan_amount': '100',
                                                                   'min_loan_amount': '500', 'max_repayment_period_in_weeks': 4, 'repayment_cycle': 'W'})
        self.assertContains(response, 'cannot be greater than the maximum')
        self.assertEqual(LoanProducts.objects.count(), 0)

    def test_loan_request_must_fit_product_limits(self):
        customer = Customer.objects.create(first_name='A', last_name='B', registration_date=date(2024, 1, 1), phone_number='07', gender='M',
                                           date_of_birth=date(1990, 1, 1), marital_status='S', address='K', occupation='T')
        guarantor = Guarantor.objects.create(first_name='G', last_name='H', phone_number='07', gender='F', date_of_birth=date(1980, 1, 1), occupation='T')
        product = LoanProducts.objects.create(product_code='EL', product_name='Emergency', max_loan_amount=Decimal('1000'),
                                              min_loan_amount=Decimal('100'), max_repayment_period_in_weeks=4, repayment_cycle='W')
        response = self.client.post(reverse('loan_request_page'), {'request_date': '2024-05-01', 'loan_product': product.id, 'loan_amount': '5000',
                                                                   'repayment_period_in_weeks': 10, 'repayment_cycle': 'W',
                                                                   'customer': customer.id, 'guarantor': guarantor.id})
        self.assertContains(response, 'loans must be between')
        self.assertContains(response, 'must be repaid within 4 weeks')
        self.assertEqual(LoanRequests.objects.count(), 0)


class RepaymentSummaryTests(TestCase):
    # here we test that the summary adds up the payments of each loan correctly

    def test_totals_and_balance(self):
        User.objects.create_user(username='teller', password='Str0ng-Pass-123')
        self.client.login(username='teller', password='Str0ng-Pass-123')
        staff = Bankstaff.objects.create(first_name='S', last_name='T', registration_date=date(2024, 1, 1), employee_number='E1', phone_number='07', gender='M',
                                         marital_status='S', address='K', number_of_dependants=0, department='L', position='O')
        customer = Customer.objects.create(first_name='A', last_name='B', registration_date=date(2024, 1, 1), phone_number='07', gender='M',
                                           date_of_birth=date(1990, 1, 1), marital_status='S', address='K', occupation='T')
        guarantor = Guarantor.objects.create(first_name='G', last_name='H', phone_number='07', gender='F', date_of_birth=date(1980, 1, 1), occupation='T')
        product = LoanProducts.objects.create(product_code='BL', product_name='B', max_loan_amount=Decimal('10000'),
                                              min_loan_amount=Decimal('1'), max_repayment_period_in_weeks=52, repayment_cycle='M')
        request_obj = LoanRequests.objects.create(request_date=date(2024, 1, 1), loan_product=product, loan_amount=Decimal('1000'),
                                                  repayment_period_in_weeks=10, repayment_cycle='M', customer=customer, guarantor=guarantor)
        paid_loan = Loans.objects.create(loan_request=request_obj, loan_officer=staff, loan_disbursement_date=date(2024, 1, 2), loan_status='A')
        unpaid_loan = Loans.objects.create(loan_request=request_obj, loan_officer=None, loan_disbursement_date=date(2024, 1, 2), loan_status='P')
        for i, amount in enumerate(['300', '200']):
            LoanPayment.objects.create(payment_reference_number=f'R{i}', payment_date=timezone.now(), payment_method='C', paid_amount=Decimal(amount),
                                       paid_by=customer, payment_for=paid_loan, processed_by=staff)

        response = self.client.get(reverse('loan_repayment_summary_page'))
        self.assertEqual(response.status_code, 200)
        loans = {loan.id: loan for loan in response.context['loans']}
        self.assertEqual(loans[paid_loan.id].total_paid, Decimal('500'))
        self.assertEqual(loans[paid_loan.id].remaining_balance, Decimal('500'))
        self.assertEqual(loans[unpaid_loan.id].total_paid, Decimal('0'))
        self.assertEqual(loans[unpaid_loan.id].remaining_balance, Decimal('1000'))


class PageTests(TestCase):
    # here we test that every page in the menu opens without errors once logged in

    def test_all_pages_open(self):
        User.objects.create_user(username='teller', password='Str0ng-Pass-123')
        self.client.login(username='teller', password='Str0ng-Pass-123')
        pages = ['home_page', 'accounts_page', 'bank_staff_page', 'customer_page', 'guarantor_page', 'loan_approvals_page',
                 'loan_payment_page', 'loan_product_page', 'loan_request_page', 'loan_view_page', 'transaction_types_page',
                 'transactions_page', 'loan_repayment_summary_page']
        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(self.client.get(reverse(page)).status_code, 200)
        # every records page opens too, even when the table is empty
        from .views import RECORD_TYPES
        for record_type in RECORD_TYPES:
            with self.subTest(record_type=record_type):
                self.assertEqual(self.client.get(reverse('record_list_page', args=[record_type])).status_code, 200)

    def test_unused_home_route_is_gone(self):
        # the Raxio_app /home route is commented out in urls.py, so Django now adds the missing slash and sends /home to our real home/ page (APPEND_SLASH)
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], reverse('home_page'))


class DashboardTests(TestCase):
    # here we test the admin dashboard from the Folder 9 lecture: static files, the sidebar, the stat cards and the striped tables

    def setUp(self):
        User.objects.create_user(username='teller', password='Str0ng-Pass-123')
        self.client.login(username='teller', password='Str0ng-Pass-123')

    def test_static_files_are_found(self):
        # these files are in the project-level static folder, which Django only searches because of STATICFILES_DIRS in settings.py
        from django.contrib.staticfiles import finders
        for path in ['css/style.css', 'css/dashboard.css', 'js/dashboard.js', 'images/e_banking_logo.jpeg']:
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))

    def test_base_template_links_the_static_files(self):
        response = self.client.get(reverse('home_page'))
        self.assertContains(response, '/static/css/style.css')
        self.assertContains(response, '/static/css/dashboard.css')
        self.assertContains(response, '/static/js/dashboard.js')

    def test_sidebar_links_and_active_page(self):
        response = self.client.get(reverse('record_list_page', args=['customer']))
        self.assertContains(response, 'class="sidenav"')
        # every sidebar link uses a route name, so it points at a real page
        for page in ['home_page', 'customer_page', 'accounts_page', 'loan_view_page', 'loan_repayment_summary_page', 'transactions_page']:
            with self.subTest(page=page):
                self.assertContains(response, f'href="{reverse(page)}"')
        # on the customer records page the Customers link is highlighted and the breadcrumb names the page
        self.assertContains(response, f'href="{reverse("customer_page")}" class="nav-link active"')
        self.assertContains(response, 'Pages / <strong>Customer Records</strong>', html=False)

    def test_login_page_has_no_sidebar(self):
        self.client.logout()
        response = self.client.get(reverse('login_page'))
        self.assertNotContains(response, 'class="sidenav"')
        self.assertNotContains(response, 'class="with-sidebar"')

    def test_stat_cards_count_the_database(self):
        customer = Customer.objects.create(first_name='John', last_name='Kato', registration_date=date(2024, 2, 1), phone_number='07', gender='M',
                                           date_of_birth=date(1990, 5, 5), marital_status='M', address='Mbale', occupation='Teacher')
        for number, balance in [('A1', '1000000'), ('A2', '250000.50')]:
            Accounts.objects.create(account_number=number, account_type='S', account_balance=Decimal(balance), customer=customer, account_open_date=date(2024, 2, 2))

        response = self.client.get(reverse('home_page'))
        self.assertEqual(response.context['customer_count'], 1)
        self.assertEqual(response.context['account_count'], 2)
        self.assertEqual(response.context['total_balance'], Decimal('1250000.50'))
        self.assertEqual(response.context['total_repaid'], Decimal('0'))
        # the money is shown with commas and 2 decimal places
        self.assertContains(response, '1,250,000.50')
        self.assertContains(response, 'Across 2 accounts')

    def test_tables_are_striped(self):
        for url in [reverse('record_list_page', args=['customer']), reverse('loan_repayment_summary_page')]:
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), 'class="table table-striped"')


class PopupTests(TestCase):
    # here we test the View / Edit / Delete icons and the popups on the records pages

    def setUp(self):
        # we reuse CrudTests' setUp, which logs in and saves one record of each table
        CrudTests.setUp(self)

    def test_records_page_shows_icons(self):
        response = self.client.get(reverse('record_list_page', args=['customer']))
        self.assertContains(response, 'class="icon-btn view" data-popup')
        self.assertContains(response, 'class="icon-btn edit" data-popup')
        self.assertContains(response, 'class="icon-btn delete"')
        self.assertContains(response, f'data-confirm-delete="{self.customer}"')
        # the popup windows and their script are on the page
        self.assertContains(response, '<dialog id="record-popup"')
        self.assertContains(response, '/static/js/popups.js')

    def test_view_popup_has_no_sidebar(self):
        response = self.client.get(reverse('record_detail_page', args=['customer', self.customer.id]) + '?popup=1')
        self.assertTemplateUsed(response, 'popup_detail.html')
        self.assertNotContains(response, 'class="sidenav"')
        self.assertContains(response, 'Teacher')

    def test_edit_popup_saves_and_redirects_to_the_list(self):
        url = reverse('edit_record_page', args=['guarantor', self.guarantor.id]) + '?popup=1'
        self.assertTemplateUsed(self.client.get(url), 'popup_edit.html')
        data = {'first_name': 'Deo', 'last_name': 'Mutaasa', 'phone_number': '0700000003', 'gender': 'M',
                'date_of_birth': '1980-01-01', 'address': 'Jinja', 'occupation': 'Trader'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('record_list_page', args=['guarantor']))
        self.guarantor.refresh_from_db()
        self.assertEqual(self.guarantor.occupation, 'Trader')

    def test_edit_popup_with_errors_stays_in_the_popup(self):
        url = reverse('edit_record_page', args=['guarantor', self.guarantor.id]) + '?popup=1'
        response = self.client.post(url, {'first_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'popup_edit.html')
        self.assertContains(response, 'This field is required.')
        # no message is left waiting for the next page
        self.assertEqual(len(list(response.wsgi_request._messages)), 0)

    def test_refused_delete_from_the_list_returns_to_the_list(self):
        response = self.client.post(reverse('delete_record_page', args=['customer', self.customer.id]), {'return_to': 'list'})
        self.assertRedirects(response, reverse('record_list_page', args=['customer']))
        self.assertTrue(Customer.objects.filter(id=self.customer.id).exists())
