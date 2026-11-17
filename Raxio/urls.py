"""
URL configuration for Raxio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ebanking_app.views import *
# UNUSED: the Raxio_app routes below are commented out, so their views are not imported any more
# from Raxio_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    # our authentication pages: the login page is the first page of the site
    path('', login_view, name='login_page'),
    path('signup/', sign_up_view, name='sign_up_page'),
    path('logout/', logout_view, name='logout_page'),
    path('home/', home_view, name='home_page'),

    # Create pages: each one shows a form to add a new record
    path('accounts/', accounts_view, name='accounts_page'),
    path('bankstaff/', bankstaff_view, name='bank_staff_page'),
    path('customer/', customer_view, name='customer_page'),
    path('guarantor/', guarantor_view, name='guarantor_page'),
    path('loanapprovals/', loanapprovals_view, name='loan_approvals_page'),
    path('loanpayment/', loanpayment_view, name='loan_payment_page'),
    path('loanproduct/', loanproduct_view, name='loan_product_page'),
    path('loanrequest/', loanrequest_view, name='loan_request_page'),
    path('loans/', loan_view, name='loan_view_page'),
    path('transactiontypes/', transactiontypes_view, name='transaction_types_page'),
    path('transactions/', transactions_view, name='transactions_page'),

    # report page: read-only summary of every loan's repayments
    path('loanrepaymentsummary/', loanrepayments_view, name='loan_repayment_summary_page'),

    # Read, Update + Delete pages shared by every table.
    # <str:record_type> captures the table name (e.g. customer) and <int:record_id> captures the row id from the URL and passes both to the view, e.g. /customer/records/, /customer/3/, /customer/3/edit/
    path('<str:record_type>/records/', record_list_view, name='record_list_page'),
    path('<str:record_type>/<int:record_id>/', record_detail_view, name='record_detail_page'),
    path('<str:record_type>/<int:record_id>/edit/', edit_record_view, name='edit_record_page'),
    path('<str:record_type>/<int:record_id>/delete/', delete_record_view, name='delete_record_page'),

    # UNUSED: these Raxio_app routes are not needed. /home clashed with our home/ page and both views render templates (index.html, submit.html) that do not exist.
    # path('home', landing_page_view, name='landing_page'),
    # path('submit/', submit_view, name='submit'),
]
