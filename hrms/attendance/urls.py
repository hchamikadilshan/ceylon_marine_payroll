from django.urls import path
from .views import MarkAttendanceMainView, ViewAttendanceByDateView, ViewAttendanceByEmployeeView,EditAttendance


urlpatterns = [
    path('mark_attendance', MarkAttendanceMainView.as_view(), name="mark_attendance_main_view"),
    path('edit_attendance', EditAttendance.as_view(),
         name="edit_attendance_view"),
    path('view_attendance_by_date', ViewAttendanceByDateView.as_view(),
         name="view_attendance_by_date_view"),
    path('view_attendance_by_employee', ViewAttendanceByEmployeeView.as_view(),
         name="view_attendance_by_employee_view"),


]
