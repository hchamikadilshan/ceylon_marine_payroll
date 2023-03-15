from django.urls import path
from .views import DashboardMainView,SalarySummaryChartData


urlpatterns = [
    path('', DashboardMainView.as_view(), name="dashboard_main_view"),
    path('get_salary_summary_data', SalarySummaryChartData.as_view(), name="get_salary_summary_data"),

]
