from django.utils import timezone

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from company.models import Company
from jobapps.models import SourceType
from position.models import JobPosition
from users.models import EmploymentStatus

User = get_user_model()


class EmploymentAuth(models.Model):
    value = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.value if self.value is not None else ''


class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, null=True, blank=True)
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
    created_date = models.DateTimeField(default=timezone.now, blank=True)
    update_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_date']


class CompanyEmploymentAuth(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    employment_auth = models.ForeignKey(EmploymentAuth, on_delete=models.CASCADE)
    value = models.BooleanField(default=False)
