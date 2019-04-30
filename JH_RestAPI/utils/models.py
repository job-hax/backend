from django.db import models

# Create your models here.
class Agreement(models.Model):
  key = models.CharField(max_length=20)
  is_html = models.BooleanField(default=True)
  value = models.TextField()