# Generated by Django 3.2.17 on 2023-03-17 10:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0018_auto_20230317_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 3, 17, 16, 23, 32, 213725)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 3, 17, 16, 23, 32, 212725)),
        ),
    ]