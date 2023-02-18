from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout

# Create your views here.
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
