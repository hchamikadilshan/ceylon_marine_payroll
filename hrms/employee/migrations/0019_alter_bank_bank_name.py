# Generated by Django 3.2.17 on 2023-04-06 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0018_alter_employee_dprtmnt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='bank_name',
            field=models.CharField(max_length=150),
        ),
    ]