from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField

from college.models import College


class AlumniHomePage(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=False, blank=False)
    header_banners = JSONField(null=True, blank=True)
    additional_banners = JSONField(null=True, blank=True)
    social_media_accounts = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)