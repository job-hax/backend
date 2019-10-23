import pytz
from rest_framework import serializers

from company.serializers import CompanySerializer
from position.serializers import JobPositionSerializer
from .models import ApplicationStatus
from .models import GoogleMail
from .models import JobApplication
from .models import JobApplicationNote, JobApplicationFile, SourceType
from .models import Source, Contact
from .models import StatusHistory


class ApplicationStatusSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return ApplicationStatus.objects.create(**validated_data)

    class Meta:
        model = ApplicationStatus
        fields = ('__all__')


class SourceTypeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return SourceType.objects.create(**validated_data)

    class Meta:
        model = SourceType
        fields = ('__all__')


class GoogleMailSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return GoogleMail.objects.create(**validated_data)

    class Meta:
        model = GoogleMail
        fields = ('subject', 'body', 'date')


class SourceSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Source.objects.create(**validated_data)

    class Meta:
        model = Source
        fields = ('id', 'value', 'image')


class JobApplicationSerializer(serializers.ModelSerializer):
    application_status = ApplicationStatusSerializer(read_only=True)
    position = JobPositionSerializer(read_only=True)
    company_object = serializers.SerializerMethodField()
    app_source = SourceSerializer(read_only=True)
    editable = serializers.SerializerMethodField()

    def get_editable(self, obj):
        if obj.msg_id is not None and obj.msg_id != '':
            return False
        return True

    def get_company_object(self, obj):
        context = self.context
        context['position'] = obj.position
        return CompanySerializer(instance=obj.company_object, many=False, context=context).data

    def create(self, validated_data):
        return JobApplication.objects.create(**validated_data)

    class Meta:
        model = JobApplication
        fields = (
            'id', 'editable', 'application_status', 'position', 'company_object', 'apply_date', 'app_source', 'is_rejected')


class JobApplicationNoteSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    update_date = serializers.SerializerMethodField()

    def get_created_date(self, obj):
        if obj.created_date is None:
            return None
        return obj.created_date.astimezone(pytz.timezone('US/Pacific'))

    def get_update_date(self, obj):
        if obj.update_date is None:
            return None
        return obj.update_date.astimezone(pytz.timezone('US/Pacific'))

    def create(self, validated_data):
        return JobApplicationNote.objects.create(**validated_data)

    class Meta:
        model = JobApplicationNote
        fields = ('id', 'description', 'created_date', 'update_date')


class JobApplicationFileSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    update_date = serializers.SerializerMethodField()

    def get_created_date(self, obj):
        if obj.created_date is None:
            return None
        return obj.created_date.astimezone(pytz.timezone('US/Pacific'))

    def get_update_date(self, obj):
        if obj.update_date is None:
            return None
        return obj.update_date.astimezone(pytz.timezone('US/Pacific'))

    def create(self, validated_data):
        return JobApplicationFile.objects.create(**validated_data)

    class Meta:
        model = JobApplicationFile
        fields = ('id', 'file', 'name', 'created_date', 'update_date')


class StatusHistorySerializer(serializers.ModelSerializer):
    application_status = ApplicationStatusSerializer(read_only=True)

    def create(self, validated_data):
        return StatusHistory.objects.create(**validated_data)

    class Meta:
        model = StatusHistory
        fields = ('application_status', 'update_date')


class ContactSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    def get_position(self, obj):
        if obj.position is not None:
            return obj.position.job_title
        return None

    def get_company(self, obj):
        if obj.company is not None:
            return obj.company.company
        return None

    def create(self, validated_data):
        return Contact.objects.create(**validated_data)

    class Meta:
        model = Contact
        fields = (
            'id', 'first_name', 'last_name', 'phone_number', 'linkedin_url', 'description', 'created_date', 'update_date', 'position',
            'company', 'email')
