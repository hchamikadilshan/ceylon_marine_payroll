# Generated by Django 3.2.17 on 2023-05-26 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_attendance_next_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='night_shift',
            field=models.BooleanField(default=False),
        ),
    ]
