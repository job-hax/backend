from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings
from college.serializers import CollegeSerializer
from company.serializers import CompanyBasicsSerializer
from major.serializers import MajorSerializer
from position.serializers import JobPositionSerializer
from utils.serializers import CountrySerializer, StateSerializer
from .models import EmploymentStatus

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField(required=False)
    user_type = serializers.SerializerMethodField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if 'detailed' not in self.context:
            del self.fields['is_admin']
            del self.fields['user_type']

    def get_is_admin(self, obj):
        if self.context.get('detailed'):
            return obj.is_staff

    def get_user_type(self, obj):
        if self.context.get('detailed'):
            return obj.user_type

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    class Meta:
        model = User
        fields = ('first_name', 'profile_photo', 'last_name', 'date_joined', 'is_admin', 'user_type')


class EmploymentStatusSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return EmploymentStatus.objects.create(**validated_data)

    class Meta:
        model = EmploymentStatus
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
        if obj.social_auth.filter(provider='google-oauth2').count() == 0:
            return False
        return True

    def get_is_linkedin_linked(self, obj):
        if obj.social_auth.filter(provider='linkedin-oauth2').count() == 0:
            return False
        return True

    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'is_demo', 'activation_key', 'key_expires',
                   'forgot_password_key', 'forgot_password_key_expires', 'approved', 'groups', 'user_permissions']
