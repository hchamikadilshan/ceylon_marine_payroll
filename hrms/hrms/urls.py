from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('dashboard/',include('dashboard.urls')),
    path('employee_management/',include('employee.urls')),
    path('attendance/', include('attendance.urls')),
    path('payroll/',include('payroll.urls')),
    path('reports/',include('reports.urls')),
    path('admin_settings/',include('adminapp.urls')),
]
