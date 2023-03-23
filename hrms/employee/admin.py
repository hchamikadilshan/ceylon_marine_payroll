from django.contrib import admin
from .models import Employee,EmployeeFinance,Bank

# Register your models here.


admin.site.register(Employee)
admin.site.register(EmployeeFinance)
admin.site.register(Bank)
