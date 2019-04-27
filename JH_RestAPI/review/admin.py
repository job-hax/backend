from django.contrib import admin
from .models import Review, CompanyEmploymentAuth
from utils.export_csv import ExportCsv

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"] 

admin.site.register(CompanyEmploymentAuth)    