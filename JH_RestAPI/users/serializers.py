from django.db import models
from .models import Profile, EmploymentStatus, EmploymentAuth
from rest_framework import serializers
from django.contrib.auth import get_user_model
from college.serializers import CollegeSerializer
from major.serializers import MajorSerializer
from company.serializers import CompanyBasicsSerializer
from position.serializers import JobPositionSerializer
from utils.serializers import CountrySerializer, StateSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return User.objects.create(**validated_data)

  class Meta:
    model = User
    fields = ('username', 'first_name', 'last_name', 'email', 'date_joined')


class EmploymentStatusSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
        return EmploymentStatus.objects.create(**validated_data)

  class Meta:
    model = EmploymentStatus
    fields = ('__all__')


class EmploymentAuthSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
        return EmploymentAuth.objects.create(**validated_data)

  class Meta:
    model = EmploymentAuth
    fields = ('__all__')


class ProfileSerializer(serializers.ModelSerializer):
  user = UserSerializer(read_only=True)
  emp_status = EmploymentStatusSerializer(read_only=True)
  college = CollegeSerializer(read_only=True)
  major = MajorSerializer(read_only=True)
  company = CompanyBasicsSerializer(read_only=True)
  country = CountrySerializer(read_only=True)
  state = StateSerializer(read_only=True)
  job_position = JobPositionSerializer(read_only=True)
  dob = serializers.DateField(format="%Y-%m-%d")
  is_google_linked = serializers.SerializerMethodField()
  is_linkedin_linked = serializers.SerializerMethodField()

  def get_is_google_linked(self, obj):
    if obj.user.social_auth.filter(provider='google-oauth2').count() == 0:
      return False
    return True

  def get_is_linkedin_linked(self, obj):
    if obj.user.social_auth.filter(provider='linkedin-oauth2').count() == 0:
      return False
    return True

  def create(self, validated_data):
      return Profile.objects.create(**validated_data)

  class Meta:
    model = Profile
    fields = ('__all__')
