# Generated by Django 3.2.17 on 2023-03-08 04:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0012_auto_20230306_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='salaryadvance',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 3, 8, 9, 37, 31, 382416)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 3, 8, 9, 37, 31, 382416)),
        ),
    ]
