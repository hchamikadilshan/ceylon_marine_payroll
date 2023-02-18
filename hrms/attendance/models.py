from django.db import models
from employee.models import Employee

# Create your models here.

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    day = models.CharField(max_length=10)
    special_holiday = models.BooleanField(default=False)
    in_time = models.CharField(max_length=5)
    out_time = models.CharField(max_length=5)
    next_day = models.BooleanField(default=False)


