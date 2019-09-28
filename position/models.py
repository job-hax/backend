from django.db import models


class JobPosition(models.Model):
    job_title = models.CharField(max_length=200, blank=False)

    class Meta:
        ordering = ['job_title']

    def __str__(self):
        return self.job_title if self.job_title is not None else ''
