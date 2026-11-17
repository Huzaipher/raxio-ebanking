from django.db import models

# Create your models here.


# UNUSED: logging in now uses Django's built-in User model (the auth_user table), which stores passwords as secure hashes. This model stored passwords as plain text, so it is commented out.
# NOTE: the ebanking_app_login table and its rows are still in db.sqlite3. Running "python manage.py makemigrations" now would create a migration that DELETES that table, so only do that when you no longer need its data.
# class Login(models.Model):
#     username = models.EmailField(max_length=30)
#     password = models.CharField(max_length=20)
#
#     # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Login object (1)'
#     def __str__(self):
#         return self.username

class Bankstaff(models.Model):
    # here we list the departments a staff member can belong to. Each pair is (value stored in the database, label shown in the dropdown). Adding choices makes Django draw this field as a dropdown in every form.
    DEPARTMENT_CHOICES = [
        ('Administration', 'Administration'),
        ('Operations', 'Operations'),
        ('Loans', 'Loans & Credit'),
        ('Customer Service', 'Customer Service'),
        ('Finance', 'Finance & Accounts'),
        ('IT', 'Information Technology'),
        ('Human Resources', 'Human Resources'),
        ('Risk & Compliance', 'Risk & Compliance'),
        ('Marketing', 'Marketing'),
                        ]

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    registration_date = models.DateField() 
    employee_number = models.CharField(max_length=7)
    phone_number = models.CharField(max_length=10)
    gender = models.CharField(
        max_length=2,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
                ]
                            )
    marital_status = models.CharField(max_length=2,
                                      choices=[
                                        ('S', 'Single'),
                                        ('M', 'Married'),
                                        ('D', 'Divorced'),
                                        ('W', 'Widowed'),
                                              ]
                        
                            )
    address = models.CharField(max_length=50)
    number_of_dependants = models.IntegerField()
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    position = models.CharField(max_length=20)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Bankstaff object (1)'
    def __str__(self):
        return f'{self.employee_number} - {self.first_name} {self.last_name}'

class Customer(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    registration_date = models.DateField() 
    phone_number = models.CharField(max_length=10)
    gender = models.CharField(
                        max_length=2,
                        choices=[
                            ('M', 'Male'),
                            ('F', 'Female'),
                                 ]
                            )
    date_of_birth = models.DateField()
    marital_status = models.CharField(max_length=2,
                            choices=[
                                ('S', 'Single'),
                                ('M', 'Married'),
                                ('D', 'Divorced'),
                                ('W', 'Widowed'),
                            ]
                        )
    address = models.CharField(max_length=50)
    occupation = models.CharField(max_length=20)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Customer object (1)'
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Accounts(models.Model):
    account_number = models.CharField(max_length=10)
    account_type = models.CharField(
                            max_length=3,
                            choices=[
                                ('S', 'Savings'),
                                ('C', 'Current'),
                                ('FD', 'Fixed Deposit'),
                            ]
                        )
    account_balance = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    account_open_date = models.DateField() 

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Accounts object (1)'
    def __str__(self):
        return f'{self.account_number} - {self.customer}'

class Guarantor(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=10)
    gender = models.CharField(
                        max_length=2,
                        choices=[
                            ('M', 'Male'),
                            ('F', 'Female'),
                        ]
                    )
    date_of_birth = models.DateField()
    # here our guarantor is allowed to leave address as blank/null, and if they do, it will default to 'N/A'
    address = models.CharField(max_length=50, blank=True, null=True, default='N/A')
    occupation = models.CharField(max_length=20)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Guarantor object (1)'
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class LoanProducts(models.Model):
    product_code = models.CharField(max_length=5)
    product_name = models.CharField(max_length=20)
    max_loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    min_loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_repayment_period_in_weeks = models.IntegerField()
    repayment_cycle = models.CharField(
                                max_length=2,
                                choices=[
                                    ('W', 'Weekly'),
                                    ('M', 'Monthly'),
                                    ('Q', 'Quarterly'),
                                ]
                            )

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'LoanProducts object (1)'
    def __str__(self):
        return f'{self.product_code} - {self.product_name}'

class LoanRequests(models.Model):
    request_date = models.DateField()
    loan_product = models.ForeignKey(LoanProducts, on_delete=models.RESTRICT)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_period_in_weeks = models.IntegerField()
    repayment_cycle = models.CharField(
                            max_length=2,
                            choices=[
                                ('W', 'Weekly'),
                                ('M', 'Monthly'),
                                ('Q', 'Quarterly'),
                                    ]
                                )
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    guarantor = models.ForeignKey(Guarantor, on_delete=models.RESTRICT)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'LoanRequests object (1)'
    def __str__(self):
        return f'Request #{self.id} - {self.customer} ({self.loan_amount})'

class Loans(models.Model):
    loan_request = models.ForeignKey(LoanRequests, on_delete=models.RESTRICT)
    loan_officer = models.ForeignKey(Bankstaff, on_delete=models.SET_NULL, null=True)
    loan_disbursement_date = models.DateField() 
    loan_status = models.CharField(
                            max_length=2,
                            choices=[
                                ('A', 'Approved'),
                                ('R', 'Rejected'),
                                ('P', 'Pending'),
                            ]
                                )

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Loans object (1)'
    def __str__(self):
        return f'Loan #{self.id} - {self.loan_request.customer}'

class LoanApprovals(models.Model):
    loan = models.ForeignKey(Loans, on_delete=models.RESTRICT)
    approval_date = models.DateField() 
    approval_status = models.CharField(
                            max_length=2,
                            choices=[
                                ('A', 'Approved'),
                                ('R', 'Rejected'),
                                ('P', 'Pending'),
                            ]
                        )
    bank_staff = models.ForeignKey(Bankstaff, on_delete=models.SET_NULL, null=True)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'LoanApprovals object (1)'
    def __str__(self):
        return f'Approval #{self.id} for Loan #{self.loan_id}'

class TransactionTypes(models.Model):
    transaction_type = models.CharField(max_length=20)
    description = models.CharField(max_length=50)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'TransactionTypes object (1)'
    def __str__(self):
        return self.transaction_type

class Transactions(models.Model):
    transaction_date = models.DateTimeField(auto_now_add=True) 
    transaction_type = models.ForeignKey(TransactionTypes, on_delete=models.RESTRICT)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    account = models.ForeignKey(Accounts, on_delete=models.RESTRICT)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'Transactions object (1)'
    def __str__(self):
        return f'{self.transaction_type} of {self.transaction_amount} on {self.account.account_number}'

# here the LoanPayment model records each repayment installment made by a customer against a loan
class LoanPayment(models.Model):
    payment_reference_number = models.CharField(max_length=20, unique=True)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(
                            max_length=2,
                            choices=[
                                ('BT', 'Bank Transfer'),
                                ('MM', 'Mobile Money'),
                                ('AB', 'Agent Banking'),
                                ('C', 'Cash'),
                            ]
                        )
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # the customer who made the payment
    paid_by = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    # the loan this payment is being made against
    payment_for = models.ForeignKey(Loans, on_delete=models.RESTRICT)
    # the staff member who received/processed the payment
    processed_by = models.ForeignKey(Bankstaff, on_delete=models.RESTRICT)

    # here the __str__ method decides how a record is displayed as text, e.g. in form dropdowns and in the admin, instead of 'LoanPayment object (1)'
    def __str__(self):
        return self.payment_reference_number
