# Generated by Django 4.1.5 on 2023-01-29 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_remove_employee_id_alter_employee_emp_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='nic_no',
            field=models.CharField(default='0', max_length=15),
        ),
    ]
