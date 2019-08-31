from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import Profile, User, EmploymentStatus, Feedback, EmploymentAuth


@admin.register(User)
class UserAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("email", "first_name", "last_name", "username")
    list_filter = ("email", "first_name", "last_name", "username")
    actions = ["export_as_csv"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("user", "user_type", "is_gmail_read_ok", "gender", "college",
                    "student_email", "phone_number", "dob")
    list_filter = ("user", "user_type", "is_gmail_read_ok", "gender", "college",
                   "student_email", "phone_number", "dob")
    actions = ["export_as_csv"]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ("user", "text", "star")
    list_filter = ("user", "text", "star")
    actions = ["export_as_csv"]


admin.site.register(EmploymentStatus)
admin.site.register(EmploymentAuth)
