from django.contrib import admin

# import all the models from the models.py file in the ebanking_app application
from .models import *

# here you can define new admin classes where you specify only the fields you want to display in the admin interface for each model. This is done by creating a new class that inherits from admin.ModelAdmin and specifying the list_display attribute with a tuple of field names.
# UNUSED: the Login model is commented out in models.py, so its admin class and registration are commented out too.
# class LoginAdmin(admin.ModelAdmin):
#     list_display = ('username', 'password')

class BankstaffAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'first_name', 'last_name', 'phone_number', 'position')
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number')
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'customer', 'account_balance', 'account_open_date')
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number')
class LoanProductsAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name')
class LoanRequestsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'loan_product', 'loan_amount', 'request_date')
class LoansAdmin(admin.ModelAdmin):
    list_display = ('loan_officer', 'loan_request', 'loan_status', 'loan_disbursement_date')
class LoanApprovalsAdmin(admin.ModelAdmin):
    list_display = ('loan', 'approval_date', 'approval_status', 'bank_staff')
class TransactionTypesAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'description')
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_date','transaction_type',  'transaction_amount')
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference_number', 'payment_date', 'payment_method', 'paid_amount', 'paid_by', 'payment_for', 'processed_by')

# here we register the models with the admin site, along with their corresponding admin classes. This allows us to customize the display of each model in the Django admin interface.
# admin.site.register(Login, LoginAdmin)
admin.site.register(Bankstaff, BankstaffAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Accounts, AccountsAdmin)
admin.site.register(Guarantor, GuarantorAdmin)
admin.site.register(LoanProducts, LoanProductsAdmin)
admin.site.register(LoanRequests, LoanRequestsAdmin)
admin.site.register(Loans, LoansAdmin)
admin.site.register(LoanApprovals, LoanApprovalsAdmin)
admin.site.register(TransactionTypes, TransactionTypesAdmin)
admin.site.register(Transactions, TransactionsAdmin)
admin.site.register(LoanPayment, LoanPaymentAdmin)
