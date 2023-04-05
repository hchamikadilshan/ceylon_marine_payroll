from django.db import models

# Create your models here.

class Department(models.Model):
    department = models.CharField(max_length=100)
