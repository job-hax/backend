from django.db import models
from django.contrib.auth.models import User
from .models import ApplicationStatus
from .models import JobApplication
from .models import GoogleMail
from rest_framework import serializers

class ApplicationStatusSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return ApplicationStatus.objects.create(**validated_data)
  class Meta:
    model = ApplicationStatus
    fields = ('__all__')

class GoogleMailSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return GoogleMail.objects.create(**validated_data)
  class Meta:
    model = GoogleMail
    fields = ('subject', 'body', 'date')    

class JobApplicationSerializer(serializers.ModelSerializer):
  applicationStatus = ApplicationStatusSerializer(read_only=True)
  def create(self, validated_data):
        return JobApplication.objects.create(**validated_data)
  class Meta:
    model = JobApplication
    fields = ('__all__')