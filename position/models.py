from django.db import models


class JobPosition(models.Model):
    job_title = models.CharField(max_length=200, blank=False)

    class Meta:
        ordering = ['job_title']
