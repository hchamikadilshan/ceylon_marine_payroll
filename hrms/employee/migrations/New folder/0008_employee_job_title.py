# Generated by Django 3.2.17 on 2023-02-14 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0007_auto_20230207_0540'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='job_title',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
