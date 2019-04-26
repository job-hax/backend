from django.contrib import admin
from .models import Company
from utils.export_csv import ExportCsv

# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]  
