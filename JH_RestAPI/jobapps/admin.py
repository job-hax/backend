from django.contrib import admin
from .models import JobApplication, ApplicationStatus, Source, JobPostDetail, GoogleMail
from utils.export_csv import ExportCsv

# Register your models here.
@admin.register(JobApplication)
class CompanyAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]  
admin.site.register(ApplicationStatus)
admin.site.register(JobPostDetail)
admin.site.register(GoogleMail)
admin.site.register(Source)
