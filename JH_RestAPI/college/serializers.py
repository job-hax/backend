from rest_framework import serializers
from .models import College, Major


class CollegeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return College.objects.create(**validated_data)

    class Meta:
        model = College
        fields = '__all__'


class MajorSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Major.objects.create(**validated_data)

    class Meta:
        model = Major
        fields = '__all__'