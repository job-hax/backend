from rest_framework import serializers

from .models import College, CollegeCoach


class CollegeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return College.objects.create(**validated_data)

    class Meta:
        model = College
        fields = '__all__'


class CollegeCoachSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return CollegeCoach.objects.create(**validated_data)

    class Meta:
        model = CollegeCoach
        fields = '__all__'
