from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import Company


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]
