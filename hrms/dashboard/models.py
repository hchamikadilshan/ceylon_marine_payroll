from django.db import models

# Create your models here.

class MonthSummary(models.Model):
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    no_of_employees = models.SmallIntegerField()
    total_salary = models.DecimalField(max_digits=10,decimal_places=2)
    total_salary_advance =  models.DecimalField(max_digits=10,decimal_places=2)
    total_allowance =  models.DecimalField(max_digits=10,decimal_places=2)
    total_epf = models.DecimalField(max_digits=10,decimal_places=2)

