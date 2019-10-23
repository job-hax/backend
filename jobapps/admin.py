from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import JobApplication, ApplicationStatus, Source, GoogleMail, SourceType, Contact, JobApplicationFile


# Register your models here.
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("user", "application_status", "position",
                    'company_object', 'app_source', 'is_deleted', 'apply_date')
    list_filter = ("user", "application_status", "position",
                   'company_object', 'app_source', 'apply_date')
    actions = ["export_as_csv"]


@admin.register(GoogleMail)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "job_post", "subject", "app_source")
    list_filter = ("user", "job_post", "subject", "app_source")


@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ("value", "pos", "rejectable", "default")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("value", "system")


@admin.register(JobApplicationFile)
class JobAppFileAdmin(admin.ModelAdmin):
    list_display = ("name", "id")


@admin.register(SourceType)
class SourceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "value")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "created_date", "update_date")
