from django.urls import path
from .views import SalaryReportView, AdvancePaymentsView, AllowancesView, EmployeeSalaryPdfView, GetAllowanceData,GetAdvancePaymentData


urlpatterns = [
    path('payroll_test', SalaryReportView.as_view(), name="payroll_test_view"),
    path('advance_payments', AdvancePaymentsView.as_view(), name="advance_payments_view"),
    path('get_advance_payment_data', GetAdvancePaymentData.as_view(),
         name="get_advance_payment_data"),
    path('get_allowance_data', GetAllowanceData.as_view(),
         name="get_allowance_data"),
    path('alllowances', AllowancesView.as_view(), name="allowances_view"),
    path("employee_salary_pdf",EmployeeSalaryPdfView.as_view(),name="employee_salary_pdf_view")
]
