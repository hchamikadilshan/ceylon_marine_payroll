# Generated by Django 3.2.17 on 2023-04-04 06:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0024_auto_20230404_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alllowance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 4, 4, 11, 46, 30, 43010)),
        ),
        migrations.AlterField(
            model_name='salaryadvance',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 4, 4, 11, 46, 30, 43010)),
        ),
    ]