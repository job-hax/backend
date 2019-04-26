from django.contrib import admin
from .models import JobApplication, ApplicationStatus, Source, JobPostDetail, GoogleMail

# Register your models here.
admin.site.register(JobApplication)
admin.site.register(ApplicationStatus)
admin.site.register(JobPostDetail)
admin.site.register(GoogleMail)
admin.site.register(Source)
