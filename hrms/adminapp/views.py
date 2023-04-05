from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Department

# Create your views here.

class AdminMainView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        departments_list = Department.objects.all()
        return render (request,"admin.html",context={'user':user,'departments':departments_list})
class AddDepartment(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        department_name = request.POST["admin_department_name"]
        department = Department(department = department_name)
        department.save()
        return redirect("admin_main_view")