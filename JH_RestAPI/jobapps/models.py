from django.db import models
from django.contrib.auth.models import User
from datetime import datetime   
from position.models import JobPosition
from company.models import Company
    
class ApplicationStatus(models.Model):
  value = models.CharField(max_length=20)
  def __str__(self):
    return self.value      

class JobApplication(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  applicationStatus = models.ForeignKey(ApplicationStatus, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='%(class)s_applicationStatus')
  position = models.ForeignKey(JobPosition, on_delete=models.DO_NOTHING, null=True, related_name='%(class)s_position')
  companyObject = models.ForeignKey(Company, on_delete=models.DO_NOTHING, null=True, related_name='%(class)s_company')
  applyDate = models.DateTimeField(blank=True)
  msgId = models.CharField(max_length=200)
  source = models.CharField(max_length=200, default='')
  isRejected = models.BooleanField(default=False)
  isDeleted = models.BooleanField(default=False)
  
  def __str__(self):
    return self.position.job_title + '@' + self.companyObject.company + '/' + str(self.applyDate)

class StatusHistory(models.Model):
  job_post = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True) 
  applicationStatus = models.ForeignKey(ApplicationStatus, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='%(class)s_applicationStatus')
  update_date = models.DateTimeField(default=datetime.now, blank=True)    

class GoogleMail(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=True)    
  job_post = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True)
  subject = models.CharField(max_length=200)
  body = models.TextField(null=True, blank=True)
  date = models.CharField(max_length=50)
  msgId = models.CharField(max_length=200, null=True)

class JobPostDetail(models.Model):
  job_post = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True) 
  posterInformation = models.TextField(null=True, blank=True)
  decoratedJobPosting = models.TextField(null=True, blank=True)
  topCardV2 = models.TextField(null=True, blank=True)

class JobApplicationNote(models.Model):
  job_post = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True) 
  description = models.TextField(null=True, blank=True)
  created_date = models.DateTimeField(default=datetime.now, blank=True) 
  update_date = models.DateTimeField(default=datetime.now, null=True, blank=True) 

