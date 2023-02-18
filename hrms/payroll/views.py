from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from employee.models import Employee
from attendance.models import Attendance
from django.db.models import Avg, Case, Count, F
from datetime import  datetime

# Create your views here.


class PayRollTestView(View):
    def get(self, request):
        return render(request, 'payroll_test.html')

    def post(self, request):
        emp_id = request.POST['emp_id']
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date__month=year_month_split[1]).order_by('date').values()
        attendance_record_list = list(attendance_record)

        for record in attendance_record_list:
            normal_working_hours = 9.0
            ot_hours = 0
            date = str(record['date']).split('-')
            in_time = str(record['in_time']).split('.')
            out_time = str(record['out_time']).split('.')
            in_time_obj = datetime(int(date[0]), int(date[1]), int(
                date[2]), int(in_time[0]), int(in_time[1]))
            out_time_obj = datetime(int(date[0]), int(date[1]), int(
                date[2]), int(out_time[0]), int(out_time[1]))
            attendance_in_time = datetime(
                int(date[0]), int(date[1]), int(date[2]), 7, 30)
            attendance_out_time = datetime(
                int(date[0]), int(date[1]), int(date[2]), 16, 30)
            attendance_out_time_noon = datetime(
                int(date[0]), int(date[1]), int(date[2]), 12, 00)

            if (in_time_obj == attendance_in_time and out_time_obj == attendance_out_time):
                pass
            # Deducting the punishment hours
            elif (in_time_obj > attendance_in_time or out_time_obj < attendance_out_time):
                if in_time_obj > attendance_in_time:
                    in_time_difference = in_time_obj - attendance_in_time
                    in_time_difference_hours = in_time_difference.total_seconds()/(60*60)
                    a = (in_time_difference.total_seconds()/(60*60))//0.5
                    b = (in_time_difference.total_seconds()/(60*60)) % 0.5
                    if in_time_difference_hours <= 0.5:
                        normal_working_hours = normal_working_hours - 0.5
                    elif in_time_difference_hours > 0.5:
                        normal_working_hours = normal_working_hours - \
                            (0.5 * a) - (0.5 if b != 0 else 0)
                if out_time_obj < attendance_out_time:
                    out_time_difference = attendance_out_time - out_time_obj
                    print(out_time_difference)
                    out_time_difference_hours = out_time_difference.total_seconds()/(60*60)
                    print(out_time_difference_hours)
                    a = (out_time_difference.total_seconds()/(60*60))//0.5
                    b = (out_time_difference.total_seconds()/(60*60)) % 0.5
                    print(a,b)
                    if out_time_difference_hours <= 0.5:
                        normal_working_hours = normal_working_hours - 0.5
                    elif out_time_difference_hours > 0.5:
                        normal_working_hours = normal_working_hours - \
                            (0.5 * a) - (0.5 if b != 0 else 0)
            if ((out_time_obj <= attendance_out_time_noon)):
                pass
            else:
                normal_working_hours = normal_working_hours -1
            record['working_hours'] = normal_working_hours
            # O/T Hours Calculation
            if (in_time_obj < attendance_in_time or out_time_obj > attendance_out_time):
                if in_time_obj < attendance_in_time :
                    in_time_difference_ot = attendance_in_time - in_time_obj
                    in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                    a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                    b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                    if in_time_difference_ot_hours <= 0.5:
                        ot_hours = ot_hours + 0.5
                    elif in_time_difference_ot_hours > 0.5:
                        ot_hours = ot_hours + (0.5 * a) + (0.5 if b != 0 else 0)
                if out_time_obj > attendance_out_time:
                    out_time_difference_ot = out_time_obj - attendance_out_time
                    out_time_difference_ot_hours = out_time_difference_ot.total_seconds()/(60*60)
                    a = (out_time_difference_ot.total_seconds()/(60*60))//0.5
                    b = (out_time_difference_ot.total_seconds()/(60*60)) % 0.5
                    if out_time_difference_ot_hours <= 0.5:
                        ot_hours = ot_hours + 0.5
                    elif out_time_difference_ot_hours > 0.5:
                        ot_hours = ot_hours + (0.5 * a) + (0.5 if b != 0 else 0)
            if record['day'] == "Saturday":
                ot_hours = ot_hours + 3
            elif record['day'] == "Sunday":
                ot_hours = ot_hours + 4
            print(record)
            print(ot_hours)
            record['ot_hours'] = ot_hours
        return JsonResponse({'attendance_list': attendance_record_list}, status=200)
