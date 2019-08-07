from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from jobapps.models import SourceType
from company.models import Company
from position.models import JobPosition
from users.models import EmploymentStatus
from users.models import EmploymentAuth
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pros = models.TextField(null=True, blank=True)
    cons = models.TextField(null=True, blank=True)
    emp_status = models.ForeignKey(EmploymentStatus, on_delete=models.SET_NULL, null=True, blank=True)
    interview_notes = models.TextField(null=True, blank=True)
    source_type = models.ForeignKey(SourceType, on_delete=models.SET_NULL, null=True, blank=True)
    overall_company_experience = models.IntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ], null=True, blank=True)
    interview_difficulty = models.IntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ], null=True, blank=True)
    overall_interview_experience = models.IntegerField(validators=[
        MaxValueValidator(1),
        MinValueValidator(0)
    ], null=True, blank=True)
    anonymous = models.BooleanField(default=False, null=False, blank=False)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    update_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_date']


class CompanyEmploymentAuth(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    employment_auth = models.ForeignKey(EmploymentAuth, on_delete=models.CASCADE)
    value = models.BooleanField(default=False)
