# Generated by Django 3.2.17 on 2023-04-04 23:16

from django.db import migrations, models
import django.db.models.deletion
import employee.models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0001_initial'),
        # ('employee', '0016_employee_dprtmnt'),
        ('employee', '0015_bank_bankbranch'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='dprtmnt',
            field=models.ForeignKey(default=employee.models.get_default_department, on_delete=django.db.models.deletion.SET_DEFAULT, to='adminapp.department'),
        ),
    ]
