from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import JobPosition


# Register your models here.
@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]
