from django.urls import path
from .views import PayRollTestView, AdvancePaymentsView, AllowancesView


urlpatterns = [
    path('payroll_test', PayRollTestView.as_view(), name="payroll_test_view"),
    path('advance_payments', AdvancePaymentsView.as_view(), name="advance_payments_view"),
    path('alllowances', AllowancesView.as_view(), name="allowances_view"),
]
