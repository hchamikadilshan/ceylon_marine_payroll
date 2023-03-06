# Generated by Django 3.2.17 on 2023-03-01 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0009_remove_employee_emp_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='address',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_acc_name',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_acc_no',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_branch',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='employee',
            name='epf_no',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='employee',
            name='mobile_no',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='employee',
            name='nic_no',
            field=models.CharField(default='', max_length=15),
        ),
    ]