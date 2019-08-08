from django.db import models


# Create your models here.


class Major(models.Model):
    name = models.CharField(max_length=200, blank=True)
    supported = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
