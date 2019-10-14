import pytz
from rest_framework import serializers
from .models import EventType, Event, EventAttendee
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, UserTypeSerializer
User = get_user_model()


class EventTypeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return EventType.objects.create(**validated_data)

    class Meta:
        model = EventType
        fields = ('__all__')


class EventAttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    def create(self, validated_data):
        return EventAttendee.objects.create(**validated_data)

    class Meta:
        model = EventAttendee
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    host_user = UserSerializer(read_only=True)
    spot_count = serializers.SerializerMethodField()
    attendee_count = serializers.SerializerMethodField()
    attended = serializers.SerializerMethodField()
    attendee_list = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    user_types = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(EventSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('user')
        if user.user_type.name != 'Career Service':
            del self.fields['user_types']

    def get_user_types(self, obj):
        if self.context.get('user').user_type.name == 'Career Service':
            return UserTypeSerializer(instance=obj.user_types, context={'basic': True}, many=True).data

    def get_mine(self, obj):
        return obj.host_user == self.context.get('user')

    def get_created_at(self, obj):
        if obj.date is None:
            return None
        return obj.date.astimezone(pytz.timezone('US/Pacific'))

    def get_event_type(self, obj):
        return EventTypeSerializer(instance=obj.event_type, many=False).data

    def get_attendee_list(self, obj):
        return EventAttendeeSerializer(instance=EventAttendee.objects.filter(event=obj, user__is_demo=False),
                                       many=True).data

    def get_attended(self, obj):
        if EventAttendee.objects.filter(event=obj, user=self.context.get('user')).count() == 0:
            return False
        return True

    def get_spot_count(self, obj):
        if obj.spot_count is None:
            return None
        return int(obj.spot_count) - EventAttendee.objects.filter(event=obj).count()

    def get_attendee_count(self, obj):
        return EventAttendee.objects.filter(event=obj).count()

    def create(self, validated_data):
        return Event.objects.create(**validated_data)

    class Meta:
        model = Event
        fields = '__all__'


class EventSimpleSerializer(serializers.ModelSerializer):
    host_user = UserSerializer(read_only=True)
    spot_count = serializers.SerializerMethodField()
    attendee_count = serializers.SerializerMethodField()
    attended = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField()
    user_types = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(EventSimpleSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('user')
        if user.user_type.name != 'Career Service':
            del self.fields['user_types']

    def get_user_types(self, obj):
        if self.context.get('user').user_type.name == 'Career Service':
            return UserTypeSerializer(instance=obj.user_types, context={'basic': True}, many=True).data

    def get_created_at(self, obj):
        if obj.date is None:
            return None
        return obj.date.astimezone(pytz.timezone('US/Pacific'))

    def get_event_type(self, obj):
        return EventTypeSerializer(instance=obj.event_type, many=False).data

    def get_attended(self, obj):
        if EventAttendee.objects.filter(event=obj, user=self.context.get('user')).count() == 0:
            return False
        return True

    def get_spot_count(self, obj):
        if obj.spot_count is None:
            return None

    def get_attendee_count(self, obj):
        return EventAttendee.objects.filter(event=obj).count()

    def create(self, validated_data):
        return Event.objects.create(**validated_data)

    class Meta:
        model = Event
        exclude = ['details']