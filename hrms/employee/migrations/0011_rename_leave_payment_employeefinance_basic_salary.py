# Generated by Django 3.2.17 on 2023-03-04 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0010_auto_20230301_1149'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeefinance',
            old_name='leave_payment',
            new_name='basic_salary',
        ),
    ]
