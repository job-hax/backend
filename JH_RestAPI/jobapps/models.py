from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from company.models import Company
from position.models import JobPosition
from users.models import EmploymentAuth
from users.models import EmploymentStatus

User = get_user_model()


class ApplicationStatus(models.Model):
    value = models.CharField(max_length=20)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.value

    class Meta:
        ordering = ['value']


class Source(models.Model):
    value = models.CharField(max_length=20)
    gmail_key = models.CharField(max_length=100, blank=True)
    system = models.BooleanField(default=False)
    image = models.CharField(null=True, max_length=200, blank=True)

    def __str__(self):
        return self.value

    class Meta:
        ordering = ['value']


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
    deleted_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now, null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
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


class Contact(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True)  # validators should be a list
    linkedin_url = models.CharField(max_length=100, blank=True, null=True)
    position = models.ForeignKey(
        JobPosition, on_delete=models.SET_NULL, null=True, related_name='%(class)s_position')
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, related_name='%(class)s_company')
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    update_date = models.DateTimeField(
        default=datetime.now, null=True, blank=True)

    def __str__(self):
        return self.name
