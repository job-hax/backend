from django.db import models
from .models import Profile
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

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

