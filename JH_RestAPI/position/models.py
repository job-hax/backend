from django.db import models

class JobPosition(models.Model):
  job_title = models.CharField(max_length=200, null=True)
  
  def __str__(self):
    return self.job_title
