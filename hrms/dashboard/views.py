from django.shortcuts import render, redirect
from django.views.generic import View


# Create your views here.

class DashboardMainView(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return redirect("login_user_url")
        else:
            return render(request, 'dashboard.html')