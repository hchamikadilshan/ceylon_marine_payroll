# Generated by Django 3.2.17 on 2023-06-29 10:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0046_auto_20230629_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 6, 29, 16, 14, 14, 18460)),
        ),
        migrations.AlterField(
            model_name='deduction',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 6, 29, 16, 14, 14, 18460)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 6, 29, 16, 14, 14, 18460)),
        ),
    ]