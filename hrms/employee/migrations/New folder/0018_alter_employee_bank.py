# Generated by Django 3.2.17 on 2023-03-17 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0017_alter_employee_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='bank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.bank'),
        ),
    ]