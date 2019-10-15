from rest_framework import serializers

from .models import College, CollegeCoach, LandingPage
from .models import HomePage, HomePageVideo


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
    videos = serializers.SerializerMethodField()

    def create(self, validated_data):
        return HomePage.objects.create(**validated_data)

    def get_additional_banners(self, obj):
        college_coaches = CollegeCoach.objects.filter(college=obj.college, is_publish=True)
        return CollegeCoachSerializer(instance=college_coaches, many=True).data

    def get_videos(self, obj):
        homepage_videos = HomePageVideo.objects.filter(college=obj.college, is_publish=True)
        return HomePageVideoSerializer(instance=homepage_videos, many=True).data

    class Meta:
        model = HomePage
        fields = '__all__'


class HomePageVideoSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return HomePageVideo.objects.create(**validated_data)

    class Meta:
        model = HomePageVideo
        fields = '__all__'


class LandingPageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return LandingPage.objects.create(**validated_data)

    class Meta:
        model = LandingPage
        fields = '__all__'