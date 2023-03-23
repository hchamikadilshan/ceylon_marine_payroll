# Generated by Django 3.2.17 on 2023-03-17 11:07

from django.db import migrations

def set_default_bank(apps, schema_editor):
    Employee = apps.get_model('employee', 'Employee')
    Bank = apps.get_model('employee', 'Bank')
    default_bank = Bank.objects.first()
    Employee.objects.update(bank=default_bank)

class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0016_employee_bank'),
    ]

    operations = [
        migrations.RunPython(set_default_bank),
    ]
