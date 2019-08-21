from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import JobApplication, ApplicationStatus, Source, GoogleMail, SourceType, Contact


# Register your models here.
@admin.register(JobApplication)
class CompanyAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("user", "application_status", "position",
                    'company_object', 'app_source', 'is_deleted', 'apply_date')
    list_filter = ("user", "application_status", "position",
                   'company_object', 'app_source', 'apply_date')
    actions = ["export_as_csv"]


@admin.register(GoogleMail)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "job_post", "subject", "app_source")
    list_filter = ("user", "job_post", "subject", "app_source")


admin.site.register(ApplicationStatus)
admin.site.register(Source)
admin.site.register(Contact)
admin.site.register(SourceType)
