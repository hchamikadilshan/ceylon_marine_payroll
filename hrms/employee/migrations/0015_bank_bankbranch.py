# Generated by Django 3.2.17 on 2023-03-17 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0014_auto_20230313_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('bank_id', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('bank_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BankBranch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch_id', models.CharField(max_length=4)),
                ('branch_name', models.CharField(max_length=100)),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.bank')),
            ],
        ),
    ]