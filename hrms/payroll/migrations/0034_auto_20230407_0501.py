# Generated by Django 3.2.17 on 2023-04-06 23:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0033_auto_20230407_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 4, 7, 5, 1, 30, 757766)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 4, 7, 5, 1, 30, 757766)),
        ),
    ]
