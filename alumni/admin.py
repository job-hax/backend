from django.contrib import admin

from .models import AlumniHomePage


@admin.register(AlumniHomePage)
class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ("college", "id")
    list_filter = ("college", "id")
