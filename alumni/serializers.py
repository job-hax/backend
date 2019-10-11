from django.contrib.auth import get_user_model
from rest_framework import serializers

from college.serializers import CollegeSerializer
from company.serializers import CompanyBasicsSerializer
from major.serializers import MajorSerializer
from position.serializers import JobPositionSerializer
from utils.serializers import CountrySerializer, StateSerializer


class AlumniSerializer(serializers.ModelSerializer):
    college = CollegeSerializer(read_only=True)
    major = MajorSerializer(read_only=True)
    company = CompanyBasicsSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    job_position = JobPositionSerializer(read_only=True)
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        if obj.is_email_public:
            return obj.email
        else:
            return None

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'first_name', 'last_name', 'email', 'college', 'major', 'company', 'country', 'state', 'job_position',
            'profile_photo', 'grad_year')