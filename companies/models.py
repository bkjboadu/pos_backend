from django.db import models
from xmlrpc.client import DateTime


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    company = models.ForeignKey(Company,related_name='branches', on_delete=models.CASCADE)
    created_at =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.company.name}"
