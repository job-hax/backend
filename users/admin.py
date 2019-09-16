from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import User, EmploymentStatus, Feedback


@admin.register(User)
class UserAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("email", "first_name", "last_name", "username")
    list_filter = ("email", "first_name", "last_name", "username")
    actions = ["export_as_csv"]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("user", "text", "star")
    list_filter = ("user", "text", "star")
    actions = ["export_as_csv"]


admin.site.register(EmploymentStatus)
