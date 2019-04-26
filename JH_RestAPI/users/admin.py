from django.contrib import admin
from .models import Profile, User, EmploymentStatus

# Register your models here.
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(EmploymentStatus)
