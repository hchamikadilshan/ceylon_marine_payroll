# Generated by Django 3.2.17 on 2023-04-04 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0001_initial'),
        ('employee', '0015_bank_bankbranch'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='dprtmnt',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='adminapp.department'),
        ),
    ]
