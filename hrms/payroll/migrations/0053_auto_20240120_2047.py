# Generated by Django 3.2.17 on 2024-01-20 15:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0052_auto_20231023_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 20, 20, 47, 26, 225226)),
        ),
        migrations.AlterField(
            model_name='deduction',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 20, 20, 47, 26, 225226)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 20, 20, 47, 26, 225226)),
        ),
    ]
