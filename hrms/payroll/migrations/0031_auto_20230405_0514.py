# Generated by Django 3.2.17 on 2023-04-04 23:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0030_auto_20230405_0453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 4, 5, 5, 14, 14, 678811)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 4, 5, 5, 14, 14, 678811)),
        ),
    ]
