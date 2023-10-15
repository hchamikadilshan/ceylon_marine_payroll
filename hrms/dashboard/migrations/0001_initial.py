# Generated by Django 3.2.17 on 2023-10-15 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonthSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4)),
                ('month', models.CharField(max_length=2)),
                ('no_of_employees', models.SmallIntegerField()),
                ('total_salary', models.FloatField()),
                ('total_salary_advance', models.FloatField()),
                ('total_allowance', models.FloatField()),
                ('total_epf', models.FloatField()),
                ('total_etf', models.FloatField()),
            ],
        ),
    ]