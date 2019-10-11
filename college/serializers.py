from rest_framework import serializers

from .models import College, CollegeCoach
from .models import HomePage


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


class HomePageSerializer(serializers.ModelSerializer):
    additional_banners = serializers.SerializerMethodField()

    def create(self, validated_data):
        return HomePage.objects.create(**validated_data)

    def get_additional_banners(self, obj):
        college_coaches = CollegeCoach.objects.filter(college=obj.college, is_publish=True)
        return CollegeCoachSerializer(instance=college_coaches, many=True).data

    class Meta:
        model = HomePage
        fields = '__all__'