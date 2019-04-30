from django.db import models
from .models import Agreement
from rest_framework import serializers


class AgreementSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return Agreement.objects.create(**validated_data)
  class Meta:
    model = Agreement
    fields = ('key', 'is_html', 'value')  