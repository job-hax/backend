from django.contrib import admin

# Register your models here.
from college.models import College, CollegeCoach
from .models import HomePage


@admin.register(HomePage)
class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ("college", "id")
    list_filter = ("college", "id")


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "country", "alpha_two_code", "state_province")
    list_filter = ("name", "short_name", "country", "alpha_two_code", "state_province")


@admin.register(CollegeCoach)
class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ("college", "first_name", "last_name", "title", "is_publish")
    list_filter = ("college", "first_name", "last_name", "title", "is_publish")
