from django.shortcuts import render,redirect
from django.views.generic import View
from django.http import JsonResponse
from employee.models import Employee
from .models import Attendance
from django.db.models import Avg, Case, Count, F
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class MarkAttendanceMainView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,"mark_attendance.html",context={'user':user})
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        day = request.POST['day']
        in_time = request.POST['time_in']
        out_time = request.POST['time_out']
        special_holiday = request.POST['special_holiday']
        next_day = request.POST['next_day']
        night_shift = request.POST['night_shift']
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date=date).exists()
        if attendance_record == False:
            attendance = Attendance(employee=emp, date=date, day=day, in_time=in_time,
                                    out_time=out_time, special_holiday=True if special_holiday == "true" else False, next_day=True if next_day == "true" else False, night_shift=True if night_shift == "true" else False)
            attendance.save() 
            response = 1 
        else:
            response = 0

        return JsonResponse({'response': response})
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
class DeleteAttendance(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        emp = Employee.objects.get(emp_id=emp_id)
        Attendance.objects.filter(employee=emp,date=date).delete()
        return JsonResponse({})
    
class EditAttendance(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        day = request.POST['day']
        in_time = request.POST['time_in']
        out_time = request.POST['time_out']
        special_holiday = request.POST['special_holiday']
        next_day = request.POST['next_day']
        night_shift = request.POST['night_shift']
        emp = Employee.objects.get(emp_id=emp_id)
        attendance = Attendance.objects.get(employee=emp,date=date)
        attendance.date = date
        attendance.day = day
        attendance.in_time= in_time
        attendance.out_time = out_time
        attendance.special_holiday = True if special_holiday == "true" else False
        attendance.next_day = True if next_day == "true" else False
        attendance.night_shift = True if night_shift == "true" else False

        attendance.save()
        return JsonResponse({})

class ViewAttendanceByEmployeeView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'view_attendance_by_employee.html',context={'user':user})
    
    def post(self,request):
        emp_id = request.POST['emp_id']
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date__month=year_month_split[1] ,date__year =year_month_split[0]).order_by('date').values()
        attendance_record_list = list(attendance_record)

        return JsonResponse({'attendance_list': attendance_record_list}, status=200)


class ViewAttendanceByDateView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self, request):
        user = request.user
        return render(request, 'view_attendance_by_date.html',context={'user':user})

    def post(self, request):
        date = request.POST["date"]
        attendance_record = Attendance.objects.filter(
            date=date).annotate(name=F('employee__name')).values()
        attendance_record_list = list(attendance_record)
        print(attendance_record_list)
        return JsonResponse({'attendance_list': attendance_record_list}, status=200)
