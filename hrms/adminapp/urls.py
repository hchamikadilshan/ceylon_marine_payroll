from django.urls import path
from .views import AdminMainView,AddDepartment


urlpatterns = [
    path('', AdminMainView.as_view(), name="admin_main_view"),
    path('add_department', AddDepartment.as_view(), name="add_department_view"),
]
