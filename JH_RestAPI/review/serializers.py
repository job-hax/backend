from django.db import models
from .models import Review, CompanyEmploymentAuth
from rest_framework import serializers
from company.serializers import CompanySerializer
from position.serializers import JobPositionSerializer
from jobapps.serializers import JobApplicationSerializer, SourceTypeSerializer
from users.serializers import EmploymentAuthSerializer, EmploymentStatusSerializer
import pytz




class CompanyEmploymentAuthSerializer(serializers.ModelSerializer):
    employment_auth = EmploymentAuthSerializer(read_only=True)

    def create(self, validated_data):
        return CompanyEmploymentAuth.objects.create(**validated_data)
    class Meta:
        model = CompanyEmploymentAuth
        fields = ('id', 'value', 'employment_auth')

class ReviewSerializer(serializers.ModelSerializer):
  company = CompanySerializer(read_only=True) 
  position = JobPositionSerializer(read_only=True)
  jobapp = JobApplicationSerializer(read_only=True)
  emp_auths = serializers.SerializerMethodField()
  emp_status = EmploymentStatusSerializer(read_only=True)
  source_type = SourceTypeSerializer(read_only=True)
  username = serializers.SerializerMethodField()

  def get_username(self, obj):
    username = 'Anonymous'
    if not obj.anonymous:
      username = obj.jobapp.user.username
    return username 

  def get_emp_auths(self, obj):
    auths = CompanyEmploymentAuth.objects.filter(review=obj)
    return CompanyEmploymentAuthSerializer(instance=auths, many=True).data

  def get_created_date(self, obj):
    if obj.created_date is None:
      return None
    return obj.created_date.astimezone(pytz.timezone('US/Pacific'))  

  def get_update_date(self, obj):
    if obj.update_date is None:
      return None
    return obj.update_date.astimezone(pytz.timezone('US/Pacific')) 

  def create(self, validated_data):
        return Review.objects.create(**validated_data)
  class Meta:
    model = Review
    fields = ('__all__')

