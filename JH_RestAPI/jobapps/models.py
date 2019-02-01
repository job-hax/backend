from django.db import models
from django.contrib.auth.models import User
    
class ApplicationStatus(models.Model):
  value = models.CharField(max_length=20)
  def __str__(self):
    return self.value      

class JobApplication(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  applicationStatus = models.ForeignKey(ApplicationStatus, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='applicationStatus')
  jobTitle = models.CharField(max_length=200)
  company = models.CharField(max_length=200)
  companyLogo = models.CharField(max_length=200, null=True, blank=True)
  applyDate = models.DateTimeField(blank=True)
  msgId = models.CharField(max_length=200)
  source = models.CharField(max_length=200, default='')
  isRejected = models.BooleanField(default=False)
  
  def __str__(self):
    return self.jobTitle + '@' + self.company

class GoogleMail(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=True)    
  job_post = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True)
  subject = models.CharField(max_length=200)
  body = models.TextField(null=True, blank=True)
  date = models.CharField(max_length=50)

class JobPostDetail(models.Model):
  job_post = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True) 
  posterInformation = models.TextField(null=True, blank=True)
  decoratedJobPosting = models.TextField(null=True, blank=True)
  topCardV2 = models.TextField(null=True, blank=True)

