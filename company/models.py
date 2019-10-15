from django.db import models


class Company(models.Model):
    company = models.CharField(max_length=200, blank=False)
    logo = models.FileField(blank=False, null=False, default='8af3c0b7-6f12-4d54-8d64-5c49f40f28fb.png')
    domain = models.CharField(max_length=50, null=True)
    location_lat = models.FloatField(blank=True, null=True)
    location_lon = models.FloatField(blank=True, null=True)
    location_address = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['company']

    def __str__(self):
        return self.company if self.company is not None else ''
