from django.utils import timezone

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext as _

from company.models import Company
from position.models import JobPosition

User = get_user_model()


class ApplicationStatus(models.Model):
    value = models.CharField(max_length=20)
    icon = models.FileField(blank=True, null=True)
    pos = models.SmallIntegerField(default='0', verbose_name=_('position'))
    rejectable = models.BooleanField(default=True)
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['value']
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
        ordering = ['pos']

    def __str__(self):
        return self.value if self.value is not None else ''


class Source(models.Model):
    value = models.CharField(max_length=20)
    gmail_key = models.CharField(max_length=100, blank=True)
    system = models.BooleanField(default=False)
    image = models.CharField(null=True, max_length=200, blank=True)

    class Meta:
        ordering = ['value']

    def __str__(self):
        return self.value if self.value is not None else ''


class JobApplication(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    application_status = models.ForeignKey(
        ApplicationStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_application_status')
    position = models.ForeignKey(
        JobPosition, on_delete=models.SET_NULL, null=True, related_name='%(class)s_position')
    company_object = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, related_name='%(class)s_company')
    apply_date = models.DateTimeField(blank=True)
    msg_id = models.CharField(max_length=200)
    app_source = models.ForeignKey(
        Source, on_delete=models.SET_NULL, null=True, related_name='%(class)s_source')
    rejected_date = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_rejected = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


class StatusHistory(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    application_status = models.ForeignKey(
        ApplicationStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_application_status')
    update_date = models.DateTimeField(default=timezone.now, blank=True)


class GoogleMail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=True)
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    app_source = models.ForeignKey(
        Source, on_delete=models.SET_NULL, null=True, related_name='%(class)s_source')
    subject = models.CharField(max_length=200)
    body = models.TextField(null=True, blank=True)
    date = models.CharField(max_length=50)
    msg_id = models.CharField(max_length=200, null=True)


class JobApplicationNote(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now, blank=True)
    update_date = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class JobApplicationFile(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(blank=False, null=True)
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now, blank=True)
    update_date = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class SourceType(models.Model):
    value = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.value if self.value is not None else ''


class Contact(models.Model):
    job_post = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
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
    created_date = models.DateTimeField(default=timezone.now, blank=True)
    update_date = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
