from django.db.models import Count
from rest_framework import serializers

from .models import Company


class CompanyBasicsSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Company.objects.create(**validated_data)

    class Meta:
        model = Company
        fields = ('id', 'company', 'logo', 'location_lat',
                  'location_lon', 'location_address')


class CompanySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Company.objects.create(**validated_data)

    class Meta:
        model = Company
        fields = ('__all__')
