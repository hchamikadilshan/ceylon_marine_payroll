from django.db import models

# Create your models here.

class MonthSummary(models.Model):
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    no_of_employees = models.SmallIntegerField()
    total_salary = models.FloatField()
    total_salary_advance =  models.FloatField()
    total_allowance =  models.FloatField()
    total_epf = models.FloatField()

