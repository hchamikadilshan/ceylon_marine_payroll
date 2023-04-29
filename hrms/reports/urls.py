from django.urls import path
from .views import SalarySignatureReport,BankTranferReport,BankTranferReportPDF,EpfCForm


urlpatterns = [
    path('salary_signature_report', SalarySignatureReport.as_view(), name="salary_signature_report"),
    path('brank_transfer_report', BankTranferReport.as_view(), name="brank_transfer_report"),
    path('brank_transfer_report_pdf', BankTranferReportPDF.as_view(), name="brank_transfer_report_pdf"),
    path('epf_c_form', EpfCForm.as_view(), name="epf_c_form"),



]
