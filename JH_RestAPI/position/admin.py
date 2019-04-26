from django.contrib import admin
from .models import JobPosition
from utils.export_csv import ExportCsv

# Register your models here.
@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]  
