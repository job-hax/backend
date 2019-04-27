from django.contrib import admin
from .models import Profile, User, EmploymentStatus, Feedback, EmploymentAuth
from utils.export_csv import ExportCsv


@admin.register(User)
class UserAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("email", "first_name", "last_name", "username")
    list_filter = ("email", "first_name", "last_name", "username")
    actions = ["export_as_csv"]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]    

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin, ExportCsv):
    actions = ["export_as_csv"]     

admin.site.register(EmploymentStatus)
admin.site.register(EmploymentAuth)
