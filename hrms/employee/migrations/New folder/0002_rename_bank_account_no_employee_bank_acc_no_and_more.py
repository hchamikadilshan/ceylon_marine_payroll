# Generated by Django 4.1.5 on 2023-01-29 01:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='bank_account_no',
            new_name='bank_acc_no',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='branch',
            new_name='bank_branch',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='date_of_termination',
            new_name='termination_date',
        ),
    ]
