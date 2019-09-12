import pytz
from rest_framework import serializers

from jobapps.serializers import SourceTypeSerializer
from users.serializers import EmploymentStatusSerializer
from .models import Review, CompanyEmploymentAuth, EmploymentAuth


class EmploymentAuthSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return EmploymentAuth.objects.create(**validated_data)

    class Meta:
        model = EmploymentAuth
        fields = ('__all__')


class CompanyEmploymentAuthSerializer(serializers.ModelSerializer):
    employment_auth = EmploymentAuthSerializer(read_only=True)

    def create(self, validated_data):
        return CompanyEmploymentAuth.objects.create(**validated_data)

    class Meta:
        model = CompanyEmploymentAuth
        fields = ('id', 'value', 'employment_auth')


class ReviewSerializer(serializers.ModelSerializer):
    emp_auths = serializers.SerializerMethodField()
    emp_status = EmploymentStatusSerializer(read_only=True)
    source_type = SourceTypeSerializer(read_only=True)
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        username = 'Anonymous'
        if not obj.anonymous and obj.user is not None:
            username = obj.user.username
        return username

    def get_emp_auths(self, obj):
        auths = CompanyEmploymentAuth.objects.filter(review=obj)
        return CompanyEmploymentAuthSerializer(instance=auths, many=True).data

    def get_created_date(self, obj):
        if obj.created_date is None:
            return None
        return obj.created_date.astimezone(pytz.timezone('US/Pacific'))

    def get_update_date(self, obj):
        if obj.update_date is None:
            return None
        return obj.update_date.astimezone(pytz.timezone('US/Pacific'))

    def create(self, validated_data):
        return Review.objects.create(**validated_data)

    class Meta:
        model = Review
        fields = ('id', 'emp_auths', 'emp_status', 'source_type', 'username', 'pros', 'cons', 'interview_notes',
                  'overall_company_experience', 'interview_difficulty', 'overall_interview_experience', 'anonymous',
                  'created_date', 'update_date', 'is_published')
