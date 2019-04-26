from django.db import models
from django.contrib.auth.models import User
from .models import Profile
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return User.objects.create(**validated_data)
  class Meta:
    model = User
    fields = ('username', 'first_name', 'last_name', 'email', 'date_joined')    

class ProfileSerializer(serializers.ModelSerializer):
  user = UserSerializer(read_only=True) 

  def create(self, validated_data):
        return Profile.objects.create(**validated_data)
  class Meta:
    model = Profile
    fields = ('__all__')

