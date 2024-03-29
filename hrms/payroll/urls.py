from django.urls import path
from .views import SalaryReportView, AdvancePaymentsView, AllowancesView, EmployeeSalaryPdfView, GetAllowanceData,GetAdvancePaymentData,EditAllowance,EditAdvancePayment,PayslipPdfView,PayslipInfo,DeductionsView,GetDeductionData,EditDeduction


urlpatterns = [
    path('payroll_test', SalaryReportView.as_view(), name="payroll_test_view"),
    path('advance_payments', AdvancePaymentsView.as_view(), name="advance_payments_view"),
    path('get_advance_payment_data', GetAdvancePaymentData.as_view(),
         name="get_advance_payment_data"),
     path('edit_advance', EditAdvancePayment.as_view(), name="edit_advance"),
    path('get_allowance_data', GetAllowanceData.as_view(),
         name="get_allowance_data"),
    path('alllowances', AllowancesView.as_view(), name="allowances_view"),
    path('edit_allowance', EditAllowance.as_view(), name="edit_allowance"),
    path("employee_salary_pdf",EmployeeSalaryPdfView.as_view(),name="employee_salary_pdf_view"),
    path("payslip_pdf",PayslipPdfView.as_view(),name="pay_slip_pdf_view"),
    path("pay_slip_info",PayslipInfo.as_view(),name="get_payslip_info"),
    path("deductions",DeductionsView.as_view(),name="deductions_view"),
    path("get_deduction_data",GetDeductionData.as_view(),name="get_deduction_data"),
    path('edit_deduction', EditDeduction.as_view(), name="edit_deduction"),

    
]
