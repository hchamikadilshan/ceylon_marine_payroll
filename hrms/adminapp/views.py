from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Department
from employee.models import Bank,BankBranch

# Create your views here.

class AdminMainView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        add_bank_branches()
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
    
def add_bank_branches():

    branches = {
        "7162": [
            {"bankID": 7162, "ID": 71, "name": "Old Moor Street"},
            {"bankID": 7162, "ID": 72, "name": "Bandaragama"},
            {"bankID": 7162, "ID": 73, "name": "Digana"},
            {"bankID": 7162, "ID": 74, "name": "Monaragala"},
            {"bankID": 7162, "ID": 75, "name": "Boralasgamuwa"},
            {"bankID": 7162, "ID": 76, "name": "Kottawa"},
            {"bankID": 7162, "ID": 77, "name": "Gothatuwa"},
            {"bankID": 7162, "ID": 78, "name": "Wariyapola"},
            {"bankID": 7162, "ID": 79, "name": "Kegalle"},
            {"bankID": 7162, "ID": 80, "name": "Tissamaharama"},
            {"bankID": 7162, "ID": 81, "name": "Narahenpita"},
            {"bankID": 7162, "ID": 82, "name": "Elpitiya"},
            {"bankID": 7162, "ID": 83, "name": "Giriulla"},
            {"bankID": 7162, "ID": 84, "name": "Weligama"},
            {"bankID": 7162, "ID": 85, "name": "Nittambuwa"},
            {"bankID": 7162, "ID": 86, "name": "Minuwangoda"},
            {"bankID": 7162, "ID": 87, "name": "Hikkaduwa"},
            {"bankID": 7162, "ID": 88, "name": "Gampola"},
            {"bankID": 7162, "ID": 89, "name": "Tangalle"},
            {"bankID": 7162, "ID": 90, "name": "Mawathagama"},
            {"bankID": 7162, "ID": 91, "name": "Avissawella"},
            {"bankID": 7162, "ID": 92, "name": "Matale"},
            {"bankID": 7162, "ID": 93, "name": "Kandy City Center"},
            {"bankID": 7162, "ID": 400, "name": "Card Center"},
            {"bankID": 7162, "ID": 500, "name": "Liberty Plaza"},
            {"bankID": 7162, "ID": 501, "name": "Wattala"},
            {"bankID": 7162, "ID": 502, "name": "Mount Lavinia"},
            {"bankID": 7162, "ID": 503, "name": "Nugegoda"},
            {"bankID": 7162, "ID": 504, "name": "Kohuwala"},
            {"bankID": 7162, "ID": 999, "name": "Head Office"}
        ],
        "7205": [
            {"bankID": 7205, "ID": 0, "name": "Head Office"},
            {"bankID": 7205, "ID": 1, "name": "Main Branch"},
            {"bankID": 7205, "ID": 999, "name": "Head Office"}
        ],
        "7296": [
            {"bankID": 7296, "ID": 1, "name": "All Branches"}
        ],
        "7384": [
            {"bankID": 7384, "ID": 1, "name": "Sri Lanka Branch"}
        ],
        
        "7472": [
            {"bankID": 7472, "ID": 2, "name": "Colombo"}
        ],
        "7737": [
            {"bankID": 7737, "ID": 1, "name": "Head Office"}
        ],
        "7782": [
            {"bankID": 7782, "ID": 1, "name": "Head Office"}
        ],
        "7807": [
            {"bankID": 7807, "ID": 1, "name": "Head Office"},
            {"bankID": 7807, "ID": 2, "name": "Virtual Branch"}
        ],
        "7816": [
            {"bankID": 7816, "ID": 1, "name": "Head Office"}
        ],
        "7825": [
            {"bankID": 7825, "ID": 1, "name": "Colombo"},
            {"bankID": 7825, "ID": 2, "name": "Kandy"},
            {"bankID": 7825, "ID": 16, "name": "Nugegoda"}
        ],
        "7834": [
            {"bankID": 7834, "ID": 1, "name": "Head Office"}
        ],
        
        
        
    }

    for bank in branches:
        bank_obj = Bank.objects.get(bank_id = bank)
        for branch in branches[bank]:
            print(branch["ID"])
            branch_obj = BankBranch(bank=bank_obj,branch_id =branch["ID"],branch_name= branch["name"])
            branch_obj.save()
    # bank_obj = Bank.objects.get(bank_id = "7214")
    # for branch in branches["7214"]:
    #     print(branch["ID"])
    #     branch_obj = BankBranch(bank=bank_obj,branch_id =branch["ID"],branch_name= branch["name"])
    #     branch_obj.save()
    print("Finish")