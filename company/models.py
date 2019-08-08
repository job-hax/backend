from django.db import models


class Company(models.Model):
    company = models.CharField(max_length=200, null=True)
    company_logo = models.CharField(max_length=200, null=True, blank=True)
    cb_name = models.CharField(max_length=200, null=True)
    cb_company_logo = models.CharField(max_length=200, null=True, blank=True)
    cb_domain = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.company

    class Meta:
        ordering = ['company']
