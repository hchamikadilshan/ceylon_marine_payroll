from django.shortcuts import render,redirect
from django.views.generic import View
from django.http import JsonResponse
from employee.models import Employee
from .models import Attendance
from django.db.models import Avg, Case, Count, F

# Create your views here.

class MarkAttendanceMainView(View):
    def get(self,request):
        return render(request,"mark_attendance.html")
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        day = request.POST['day']
        in_time = request.POST['time_in']
        out_time = request.POST['time_out']
        special_holiday = request.POST['special_holiday']
        next_day = request.POST['next_day']
        emp = Employee.objects.get(emp_id=emp_id)
        attendance = Attendance(employee=emp, date=date, day=day, in_time=in_time,
                                out_time=out_time, special_holiday=True if special_holiday == "true" else False, next_day=True if next_day == "true" else False)
        attendance.save()
        return JsonResponse({})
    # def post(self,request):
    #     attendance_time_in =  []
    #     attendance_time_out = []
    #     attendance_date = []
    #     attendance_day = []
    #     emp_id = request.POST['attendance_emp_id']
    #     emp = Employee.objects.get(emp_id=emp_id)
    #     for id in request.POST:
    #         if "in" in id.split("_"):
    #             attendance_time_in.append(id)
    #         elif "out" in id.split("_"):
    #             attendance_time_out.append(id)
    #         elif "date" in id.split("_"):
    #             attendance_date.append(id)
    #         elif "day" in id.split("_"):
    #             attendance_day.append(id)
    #     i = 0
    #     while i < len(attendance_time_in):
    #         date = request.POST[attendance_date[i]]
    #         day = request.POST[attendance_day[i]]
    #         time_in = request.POST[attendance_time_in[i]]
    #         time_out = request.POST[attendance_time_out[i]]
    #         i +=1
    #         print(emp, date, day, time_in, time_out)
    #         attendance = Attendance(
    #             employee=emp, date=date, day=day, in_time=time_in, out_time=time_out)
    #         attendance.save()

    #     return redirect('mark_attendance_main_view')


class ViewAttendanceByEmployeeView(View):
    def get(self,request):
        return render(request,'view_attendance_by_employee.html')
    
    def post(self,request):
        emp_id = request.POST['emp_id']
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date__month=year_month_split[1]).order_by('date').values()
        attendance_record_list = list(attendance_record)

        return JsonResponse({'attendance_list': attendance_record_list}, status=200)


class ViewAttendanceByDateView(View):
    def get(self, request):
        return render(request, 'view_attendance_by_date.html')

    def post(self, request):
        date = request.POST["date"]
        attendance_record = Attendance.objects.filter(
            date=date).annotate(name=F('employee__name')).values()
        attendance_record_list = list(attendance_record)
        print(attendance_record_list)
        return JsonResponse({'attendance_list': attendance_record_list}, status=200)
