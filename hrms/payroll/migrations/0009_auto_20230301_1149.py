# Generated by Django 3.2.17 on 2023-03-01 06:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0008_auto_20230223_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='alllowance',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 3, 1, 11, 49, 32, 319948)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 3, 1, 11, 49, 32, 319948)),
        ),
    ]