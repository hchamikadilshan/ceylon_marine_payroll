from django.urls import path
from .views import PayRollTestView


urlpatterns = [
    path('payroll_test', PayRollTestView.as_view(), name="payroll_test_view"),
]
