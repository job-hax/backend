from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import Review, CompanyEmploymentAuth, EmploymentAuth


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("company", "position", "user", 'created_date', "is_published")
    list_filter = ("company", "position", "user", 'created_date', "is_published")
    actions = ["export_as_csv"]


@admin.register(EmploymentAuth)
class EmploymentAuthAdmin(admin.ModelAdmin):
    list_display = ("id", "value")


admin.site.register(CompanyEmploymentAuth)
