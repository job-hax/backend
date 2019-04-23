from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Company.objects.create(**validated_data)
    class Meta:
        model = Company
        fields = ('__all__')