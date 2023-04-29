from django.db import models

# Create your models here.

class Department(models.Model):
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.department
    
class Company(models.Model):
    name = models.CharField(max_length=100,blank=True)
    epf_no = models.CharField(max_length=20,blank=True)
    address = models.CharField(max_length=100,blank=True)
    bank_branch = models.CharField(max_length=100,blank=True)
    contact_no = models.CharField(max_length=15,blank=True)
    email = models.CharField(max_length=50,blank=True)