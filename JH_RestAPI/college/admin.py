from django.contrib import admin

# Register your models here.
from college.models import College, Major


@admin.register(College)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "alpha_two_code", "state_province")
    list_filter = ("name", "country", "alpha_two_code", "state_province")


admin.site.register(Major)