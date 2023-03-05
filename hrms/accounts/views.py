from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

# Create your views here.
class MyAccountDetailsView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'my_account.html' ,context={'user':user})
class EditUserAccountDetails(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username= request.POST['username']
        email = request.POST['email']

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        user.save()
        return redirect('my_account_view')
class MainView(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return redirect("login_user_url")
        else:
            return render(request, 'main.html')

class LoginUserView(View):
    def get(self,request):
        return render (request,'login.html')

    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard_main_view')
    
        else:
            return redirect('login_user_url')


class LogoutUserView(View):
    def get(self,request):
        print("inside logout")
        logout(request)
        return redirect("login_user_url")
        
    def post(self,request):
        print("inside logout")
        logout(request)
        return redirect("login_user_url")
