from django.db import models
from .models import Profile, EmploymentStatus, EmploymentAuth
from rest_framework import serializers
from django.contrib.auth import get_user_model
from college.serializers import CollegeSerializer, MajorSerializer
from company.serializers import CompanyBasicsSerializer
from position.serializers import JobPositionSerializer

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
  job_position = JobPositionSerializer(read_only=True)
  dob = serializers.DateField(format="%Y-%m-%d")

  def create(self, validated_data):
        return Profile.objects.create(**validated_data)

  class Meta:
    model = Profile
    fields = ('__all__')
