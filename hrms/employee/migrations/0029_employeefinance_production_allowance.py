# Generated by Django 3.2.17 on 2023-10-23 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0028_alter_employeefinance_morning_ot'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeefinance',
            name='production_allowance',
            field=models.FloatField(default=0),
        ),
    ]