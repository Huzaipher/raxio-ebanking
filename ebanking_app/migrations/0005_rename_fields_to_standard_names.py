# Written by hand (not by makemigrations) so that:
#  - each field is RENAMED and keeps its data, instead of being deleted and re-created empty
#  - the commented-out Login model's table is NOT deleted (makemigrations would have added that too)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebanking_app', '0004_alter_loanpayment_processed_by'),
    ]

    operations = [
        # Bankstaff
        migrations.RenameField(model_name='bankstaff', old_name='fname', new_name='first_name'),
        migrations.RenameField(model_name='bankstaff', old_name='lname', new_name='last_name'),
        migrations.RenameField(model_name='bankstaff', old_name='employee_no', new_name='employee_number'),
        migrations.RenameField(model_name='bankstaff', old_name='phone_no', new_name='phone_number'),
        migrations.RenameField(model_name='bankstaff', old_name='no_of_dependants', new_name='number_of_dependants'),
        # department becomes a dropdown. The stored values stay the same text, so existing rows (Operations, IT, Administration) are still valid.
        migrations.AlterField(
            model_name='bankstaff',
            name='department',
            field=models.CharField(choices=[('Administration', 'Administration'), ('Operations', 'Operations'), ('Loans', 'Loans & Credit'), ('Customer Service', 'Customer Service'), ('Finance', 'Finance & Accounts'), ('IT', 'Information Technology'), ('Human Resources', 'Human Resources'), ('Risk & Compliance', 'Risk & Compliance'), ('Marketing', 'Marketing')], max_length=20),
        ),

        # Customer
        migrations.RenameField(model_name='customer', old_name='fname', new_name='first_name'),
        migrations.RenameField(model_name='customer', old_name='lname', new_name='last_name'),
        migrations.RenameField(model_name='customer', old_name='phone_no', new_name='phone_number'),
        migrations.RenameField(model_name='customer', old_name='customer_date_of_birth', new_name='date_of_birth'),

        # Accounts
        migrations.RenameField(model_name='accounts', old_name='account_no', new_name='account_number'),

        # Guarantor
        migrations.RenameField(model_name='guarantor', old_name='fname', new_name='first_name'),
        migrations.RenameField(model_name='guarantor', old_name='lname', new_name='last_name'),
        migrations.RenameField(model_name='guarantor', old_name='phone_no', new_name='phone_number'),
        migrations.RenameField(model_name='guarantor', old_name='guarantor_date_of_birth', new_name='date_of_birth'),

        # LoanPayment
        migrations.RenameField(model_name='loanpayment', old_name='payment_ref_number', new_name='payment_reference_number'),
    ]
