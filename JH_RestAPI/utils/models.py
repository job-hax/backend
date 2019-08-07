from django.db import models


# Create your models here.
class Agreement(models.Model):
    key = models.CharField(max_length=20)
    is_html = models.BooleanField(default=True)
    value = models.TextField()


class Country(models.Model):
    code2 = models.CharField(max_length=10, blank=True)
    code3 = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=200, blank=True)
    capital = models.CharField(max_length=200, blank=True)
    region = models.CharField(max_length=200, blank=True)
    subregion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class State(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=200, blank=True)
    subdivision = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
