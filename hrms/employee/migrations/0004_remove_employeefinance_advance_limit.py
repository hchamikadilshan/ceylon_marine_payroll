# Generated by Django 3.2.17 on 2023-02-18 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_alter_employeefinance_submit_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeefinance',
            name='advance_limit',
        ),
    ]
