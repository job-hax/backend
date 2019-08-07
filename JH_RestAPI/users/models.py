from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from company.models import Company
from college.models import College
from major.models import Major
from utils.models import Country, State
from position.models import JobPosition
from enum import IntEnum


class EmploymentStatus(models.Model):
    value = models.CharField(max_length=20, default='N/A')

    def __str__(self):
        return self.value


class EmploymentAuth(models.Model):
    value = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.value


class User(AbstractUser):
    objects = UserManager()
    email = models.EmailField(('email address'), unique=True)
    approved = models.BooleanField(default=False, null=False)
    activation_key = models.TextField(null=True, blank=True)
    key_expires = models.DateTimeField(null=True, blank=True)
    forgot_password_key = models.TextField(null=True, blank=True)
    forgot_password_key_expires = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

# Create your models here.


class Profile(models.Model):
    User = get_user_model()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gmail_last_update_time = models.IntegerField(default=0)
    USER_TYPE_CHOICES = (
        (0, 'NONE'),
        (1, 'PUBLIC'),
        (2, 'STUDENT'),
        (3, 'ALUMNI'),
        (4, 'CAREER SERVICE'),
    )
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=0)
    is_gmail_read_ok = models.BooleanField(default=True)
    synching = models.BooleanField(default=False)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'None'),
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='N')
    dob = models.DateField(blank=True, null=True)
    student_email = models.EmailField(
        ('student email address'), unique=False, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    profile_photo_social = models.CharField(max_length=200, blank=True)
    profile_photo_custom = models.FileField(blank=True, null=True)
    emp_status = models.ForeignKey(
        EmploymentStatus, on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey(
        College, on_delete=models.SET_NULL, null=True, blank=True)
    major = models.ForeignKey(
        Major, on_delete=models.SET_NULL, null=True, blank=True)
    grad_year = models.IntegerField(null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True)
    job_position = models.ForeignKey(
        JobPosition, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, blank=True)

    class UserTypes(IntEnum):
        none = 0
        public = 1
        student = 2
        alumni = 3
        career_service = 4

    def __str__(self):
        return self.user.username

    def is_student(self):
        return self.user_type == 2

    def is_alumni(self):
        return self.user_type == 3

    def is_career_service(self):
        return self.user_type == 4


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Feedback(models.Model):
    User = get_user_model()
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    star = models.IntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ], null=True, blank=True)
