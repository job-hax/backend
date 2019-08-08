from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings
from college.serializers import CollegeSerializer
from company.serializers import CompanyBasicsSerializer
from major.serializers import MajorSerializer
from position.serializers import JobPositionSerializer
from utils.serializers import CountrySerializer, StateSerializer
from .models import Profile, EmploymentStatus, EmploymentAuth

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    def get_profile_photo(self, obj):
        profile = Profile.objects.get(user=obj)
        if profile.profile_photo_custom.name:
            return settings.MEDIA_URL + profile.profile_photo_custom.name
        elif profile.profile_photo_social is not None:
            return profile.profile_photo_social
        return None

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'profile_photo', 'last_name', 'email', 'date_joined')


class EmploymentStatusSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return EmploymentStatus.objects.create(**validated_data)

    class Meta:
        model = EmploymentStatus
        fields = ('__all__')


class EmploymentAuthSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return EmploymentAuth.objects.create(**validated_data)

    class Meta:
        model = EmploymentAuth
        fields = ('__all__')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    emp_status = EmploymentStatusSerializer(read_only=True)
    college = CollegeSerializer(read_only=True)
    major = MajorSerializer(read_only=True)
    company = CompanyBasicsSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    job_position = JobPositionSerializer(read_only=True)
    dob = serializers.DateField(format="%Y-%m-%d")
    is_google_linked = serializers.SerializerMethodField()
    is_linkedin_linked = serializers.SerializerMethodField()

    def get_is_google_linked(self, obj):
        if obj.user.social_auth.filter(provider='google-oauth2').count() == 0:
            return False
        return True

    def get_is_linkedin_linked(self, obj):
        if obj.user.social_auth.filter(provider='linkedin-oauth2').count() == 0:
            return False
        return True

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)

    class Meta:
        model = Profile
        fields = ('__all__')
