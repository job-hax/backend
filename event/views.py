import uuid
from datetime import datetime

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db.models import Q

from JH_RestAPI import pagination
from event.models import Event, EventType, EventAttendee
from event.serializers import EventSerializer, EventSimpleSerializer, EventTypeSerializer
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request, send_notification_email_to_admins

User = get_user_model()


@csrf_exempt
@api_view(["GET", "POST", "PUT", "DELETE"])
def events(request):
    if request.method == "GET":
        attended = get_boolean_from_request(request, 'attended')
        if not attended:
            user_profile = request.user
            queryset = Event.objects.filter(Q(is_approved=True) | Q(host_user=request.user),
                                            Q(host_user__user_type=user_profile.user_type) | Q(host_user__is_staff=True))
        else:
            attended_events = EventAttendee.objects.filter(user=request.user)
            queryset = Event.objects.all().filter(id__in=[e.event.id for e in attended_events])
        queryset = queryset.filter(host_user__isnull=False)
        paginator = pagination.CustomPagination()
        event_list = paginator.paginate_queryset(queryset, request)
        serialized_events = EventSimpleSerializer(
            instance=event_list, many=True, context={'user': request.user, 'detailed': False}).data
        return JsonResponse(create_response(data=serialized_events, paginator=paginator), safe=False)
    elif request.method == "DELETE":
        body = request.data
        event = Event.objects.get(pk=body['event_id'], host_user=request.user)
        event.delete()
        return JsonResponse(create_response(data=None), safe=False)
    else:
        user_profile = request.user
        if not user_profile.user_type.event_creation_enabled:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                                safe=False)
        body = request.data
        if request.method == "POST":
            event = Event()
        else:
            event = Event.objects.get(pk=body['event_id'])
            event.updated_at = datetime.now()

        event.host_user = request.user
        if 'title' in body:
            event.title = body['title']
        if 'short_description' in body:
            event.short_description = body['short_description']
        if 'details' in body:
            event.details = body['details']
        if 'location_lat' in body:
            event.location_lat = body['location_lat']
        if 'location_lon' in body:
            event.location_lon = body['location_lon']
        if 'location_address' in body:
            event.location_address = body['location_address']
        if 'event_date_start' in body:
            event.event_date_start = body['event_date_start']
        if 'event_date_end' in body:
            event.event_date_end = body['event_date_end']
        if 'event_type_id' in body:
            event.event_type = EventType.objects.get(pk=body['event_type_id'])
        if 'spot_count' in body:
            event.spot_count = body['spot_count']
        if 'header_image' in body:
            file = body['header_image']
            ext = file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)
            event.header_image.save(filename, file, save=True)
        if 'is_publish' in body:
            event.is_publish = get_boolean_from_request(request, 'is_publish')
        event.is_approved = False
        event.save()
        send_notification_email_to_admins('event')
        return JsonResponse(create_response(data={"id": event.id}), safe=False)


@csrf_exempt
@api_view(["GET"])
def event(request, event_pk):
    obj = Event.objects.get(pk=event_pk)
    serialized_event = EventSerializer(
            instance=obj, many=False, context={'user': request.user, 'detailed': True}).data
    return JsonResponse(create_response(data=serialized_event), safe=False)


@csrf_exempt
@api_view(["POST"])
def attend(request, event_pk):
    obj = Event.objects.get(pk=event_pk)
    attendance = EventAttendee()
    attendance.user = request.user
    attendance.event = obj
    attendance.save()
    return JsonResponse(create_response(data=None), safe=False)


@csrf_exempt
@api_view(["POST"])
def leave(request, event_pk):
    event_attendance = EventAttendee.objects.filter(user=request.user, event__pk=event_pk)
    if event_attendance.count() > 0:
        for event in event_attendance:
            event.delete()
    return JsonResponse(create_response(data=None), safe=False)


@csrf_exempt
@api_view(["GET"])
def types(request):
    event_types = EventType.objects.all()
    return JsonResponse(create_response(data=EventTypeSerializer(instance=event_types, many=True).data), safe=False)