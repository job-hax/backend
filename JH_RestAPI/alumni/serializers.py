from rest_framework import serializers
from users.models import Profile
from college.serializers import CollegeSerializer, MajorSerializer
from company.serializers import CompanyBasicsSerializer
from position.serializers import JobPositionSerializer
from utils.serializers import CountrySerializer, StateSerializer
from users.serializers import UserSerializer, EmploymentStatusSerializer


class AlumniSerializer(serializers.ModelSerializer):
  first_name = serializers.SerializerMethodField()
  last_name = serializers.SerializerMethodField()
  email = serializers.SerializerMethodField()
  college = CollegeSerializer(read_only=True)
  major = MajorSerializer(read_only=True)
  company = CompanyBasicsSerializer(read_only=True)
  country = CountrySerializer(read_only=True)
  state = StateSerializer(read_only=True)
  job_position = JobPositionSerializer(read_only=True)

  def get_first_name(self, obj):
    return obj.user.first_name

  def get_last_name(self, obj):
    return obj.user.last_name

  def get_email(self, obj):
    return obj.user.email

  class Meta:
    model = Profile
    fields = ('id', 'first_name', 'last_name', 'email', 'college', 'major', 'company', 'country', 'state', 'job_position', 'phone_number',\
              'profile_photo_social', 'profile_photo_custom', 'grad_year')

