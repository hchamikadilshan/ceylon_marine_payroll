# Generated by Django 3.2.17 on 2023-02-21 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0005_auto_20230219_0914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeefinance',
            name='fixed_allowance',
        ),
    ]