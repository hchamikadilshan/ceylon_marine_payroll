# Generated by Django 3.2.17 on 2023-03-17 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0019_auto_20230317_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='bank',
            field=models.ForeignKey(default='7010', on_delete=django.db.models.deletion.CASCADE, to='employee.bank'),
        ),
    ]
