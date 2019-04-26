from django.db import models
from django.contrib.auth.models import User
from .models import ApplicationStatus
from .models import JobApplication
from .models import GoogleMail
from .models import JobPostDetail
from .models import StatusHistory
from .models import Source
from .models import JobApplicationNote
from rest_framework import serializers
from position.serializers import JobPositionSerializer
from company.serializers import CompanySerializer
import pytz


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

class SourceSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return Source.objects.create(**validated_data)
  class Meta:
    model = Source
    fields = ('id', 'value')    

class JobApplicationSerializer(serializers.ModelSerializer):
  applicationStatus = ApplicationStatusSerializer(read_only=True)
  position = JobPositionSerializer(read_only=True)
  companyObject = CompanySerializer(read_only=True)
  app_source = SourceSerializer(read_only=True)
  def create(self, validated_data):
        return JobApplication.objects.create(**validated_data)
  class Meta:
    model = JobApplication
    fields = ('id', 'applicationStatus', 'position', 'companyObject', 'applyDate', 'app_source', 'isRejected')

class JobApplicationNoteSerializer(serializers.ModelSerializer):
  created_date = serializers.SerializerMethodField()
  update_date = serializers.SerializerMethodField()

  def get_created_date(self, obj):
    if obj.created_date is None:
      return None
    return obj.created_date.astimezone(pytz.timezone('US/Pacific'))  

  def get_update_date(self, obj):
    if obj.update_date is None:
      return None
    return obj.update_date.astimezone(pytz.timezone('US/Pacific')) 

  def create(self, validated_data):
        return JobApplicationNote.objects.create(**validated_data)
  class Meta:
    model = JobApplicationNote
    fields = ('id', 'description', 'created_date', 'update_date')    

class StatusHistorySerializer(serializers.ModelSerializer):
  applicationStatus = ApplicationStatusSerializer(read_only=True)
  def create(self, validated_data):
        return StatusHistory.objects.create(**validated_data)
  class Meta:
    model = StatusHistory
    fields = ('applicationStatus','update_date')       

class JobAppllicationDetailSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return JobPostDetail.objects.create(**validated_data)
  class Meta:
    model = JobPostDetail
    fields = ('posterInformation', 'decoratedJobPosting', 'topCardV2')

 
