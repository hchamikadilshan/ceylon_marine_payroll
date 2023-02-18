# Generated by Django 3.2.17 on 2023-02-14 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('day', models.CharField(max_length=10)),
                ('in_time', models.CharField(max_length=5)),
                ('out_time', models.CharField(max_length=5)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
            ],
        ),
    ]
