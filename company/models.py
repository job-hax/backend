from django.db import models


class Company(models.Model):
    company = models.CharField(max_length=200, blank=False)
    company_logo = models.CharField(max_length=200, null=True, blank=True)
    cb_name = models.CharField(max_length=200, null=True)
    cb_company_logo = models.CharField(max_length=200, null=True, blank=True)
    cb_domain = models.CharField(max_length=50, null=True)
    location_lat = models.FloatField(blank=True, null=True)
    location_lon = models.FloatField(blank=True, null=True)
    location_address = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['company']

    def __str__(self):
        return self.company if self.company is not None else ''
