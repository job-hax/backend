from django.db import models
from django.contrib.auth.models import User
from .models import ApplicationStatus
from .models import JobApplication
from .models import GoogleMail
from .models import StatusHistory
from .models import Source
from .models import JobApplicationNote, SourceType
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

class SourceTypeSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return SourceType.objects.create(**validated_data)
  class Meta:
    model = SourceType
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
    fields = ('id', 'value', 'image')    

class JobApplicationSerializer(serializers.ModelSerializer):
  applicationStatus = ApplicationStatusSerializer(read_only=True)
  position = JobPositionSerializer(read_only=True)
  companyObject = serializers.SerializerMethodField()
  app_source = SourceSerializer(read_only=True)
  editable = serializers.SerializerMethodField()

  def get_editable(self, obj):
    if obj.msgId is not None and obj.msgId != '':
      return False
    return True

  def get_companyObject(self, obj):
    context = self.context
    context['position'] = obj.position
    return CompanySerializer(instance=obj.companyObject, many=False, context=context).data

  def create(self, validated_data):
        return JobApplication.objects.create(**validated_data)
  class Meta:
    model = JobApplication
    fields = ('id', 'editable', 'applicationStatus', 'position', 'companyObject', 'applyDate', 'app_source', 'isRejected')

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

 
