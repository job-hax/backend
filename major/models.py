from django.db import models


class Major(models.Model):
    name = models.CharField(max_length=200, blank=True)
    supported = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
