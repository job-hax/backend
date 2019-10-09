from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField

from college.models import College


class AlumniHomePage(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=False, blank=False)
    banners = ArrayField(JSONField(null=True, blank=True), blank=True, null=True)
    secondary_banners = ArrayField(JSONField(null=True, blank=True), blank=True, null=True)
    social_accounts = ArrayField(JSONField(null=True, blank=True), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)