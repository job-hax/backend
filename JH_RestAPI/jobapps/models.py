from django.db import models
from datetime import datetime
from position.models import JobPosition
from company.models import Company
from users.models import EmploymentStatus
from users.models import EmploymentAuth
from JH_RestAPI import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class ApplicationStatus(models.Model):
    value = models.CharField(max_length=20)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class Source(models.Model):
    value = models.CharField(max_length=20)
    gmail_key = models.CharField(max_length=100, blank=True)
    system = models.BooleanField(default=False)
    image = models.CharField(null=True, max_length=200, blank=True)

    def __str__(self):
        return self.value


class JobApplication(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    applicationStatus = models.ForeignKey(
        ApplicationStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_applicationStatus')
    position = models.ForeignKey(
        JobPosition, on_delete=models.SET_NULL, null=True, related_name='%(class)s_position')
    companyObject = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, related_name='%(class)s_company')
    applyDate = models.DateTimeField(blank=True)
    msgId = models.CharField(max_length=200)
    app_source = models.ForeignKey(
        Source, on_delete=models.SET_NULL, null=True, related_name='%(class)s_source')
    rejected_date = models.DateTimeField(null=True, blank=True)
    isRejected = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)


class StatusHistory(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    applicationStatus = models.ForeignKey(
        ApplicationStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_applicationStatus')
    update_date = models.DateTimeField(default=datetime.now, blank=True)


class GoogleMail(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=True)
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    app_source = models.ForeignKey(
        Source, on_delete=models.SET_NULL, null=True, related_name='%(class)s_source')
    subject = models.CharField(max_length=200)
    body = models.TextField(null=True, blank=True)
    date = models.CharField(max_length=50)
    msgId = models.CharField(max_length=200, null=True)


class JobApplicationNote(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    update_date = models.DateTimeField(
        default=datetime.now, null=True, blank=True)


class SourceType(models.Model):
    value = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.value
