from django.urls import path
from .views import SalarySignatureReport


urlpatterns = [
    path('salary_signature_report', SalarySignatureReport.as_view(), name="salary_signature_report"),



]
