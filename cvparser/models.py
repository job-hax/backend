from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Resume(models.Model):
    contact = ArrayField(models.TextField(null=True, blank=True))
    skills = ArrayField(models.TextField(null=True, blank=True))
    linkedin = models.CharField(max_length=200, blank=False)
    certifications = ArrayField(models.TextField(null=True, blank=True))
    summary = ArrayField(models.TextField(null=True, blank=True))
    languages = ArrayField(models.TextField(null=True, blank=True))
    school=models.CharField(max_length=200, blank=False)
    degree=models.CharField(max_length=200, blank=False)
    company=models.CharField(max_length=200, blank=False)
    position=models.CharField(max_length=200, blank=False)
    startdate=models.CharField(max_length=200, blank=False)
    enddate=models.CharField(max_length=200, blank=False)



    class Meta:
        ordering = ['linkedin']

    def __str__(self):
        return self.name if self.name is not None else ''
