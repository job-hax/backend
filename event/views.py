import uuid
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db.models import Q

from JH_RestAPI import pagination
from event.models import Event, EventType, EventAttendee
from event.serializers import EventSerializer, EventSimpleSerializer, EventTypeSerializer
from users.serializers import UserTypeSerializer
from utils.error_codes import ResponseCodes
from users.models import UserType
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request, send_notification_email_to_admins

User = get_user_model()


@csrf_exempt
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def events(request):
    if request.method == "GET":
        if request.user.user_type.name == 'Career Service' and get_boolean_from_request(request, 'waiting'):
            queryset = Event.objects.filter(is_approved=False, is_publish=True, is_rejected=False, college=request.user.college).order_by('-updated_at')
        elif request.user.user_type.name == 'Career Service' and request.GET.get('type', '') != '':
            queryset = Event.objects.filter(Q(is_publish=True, is_rejected=False, is_approved=True) | Q(host_user=request.user),
                                            host_user__user_type__id=int(request.GET.get('type')), college=request.user.college).order_by('-updated_at')
        else:
            attended = get_boolean_from_request(request, 'attended')
            if not attended:
                user_profile = request.user
                if user_profile.user_type.name == 'Career Service':
                    student = get_boolean_from_request(request, 'student')
                    if student:
                        user_type = UserType.objects.get(name='Student')
                    else:
                        user_type = UserType.objects.get(name='Alumni')
                    queryset = Event.objects.filter(is_approved=True, is_publish=True, college=user_profile.college, user_types__in=[user_type])
                else:
                    if user_profile.user_type.name == 'Public':
                        queryset = Event.objects.filter(Q(is_approved=True, is_publish=True) | Q(host_user=request.user),
                                                        Q(user_types__in=[user_profile.user_type])
                                                        | Q(host_user__is_superuser=True))
                    else:
                        queryset = Event.objects.filter(Q(is_approved=True, is_publish=True) | Q(host_user=request.user),
                                                        Q(user_types__in=[user_profile.user_type], college=user_profile.college)
                                                        | Q(host_user__is_superuser=True))
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
    elif request.method == "PATCH":
        if request.user.user_type.name == 'Career Service':
            body = request.data
            event = Event.objects.get(pk=body['event_id'])
            approved = body['approved']
            event.is_approved = approved
            event.is_rejected = not approved
            event.save()
            return JsonResponse(create_response(data=None), safe=False)
        else:
            return JsonResponse(
                create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                safe=False)
    else:
        user_profile = request.user
        if not user_profile.user_type.event_creation_enabled:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                                safe=False)
        body = request.data
        if request.method == "POST":
            event = Event()

            if request.user.user_type.name != 'Career Service':
                event.user_types.add(request.user.user_type)
            else:
                event.save()
                user_types = body['user_types'].split(',')
                for type in user_types:
                    user_type = UserType.objects.get(pk=type)
                    event.user_types.add(user_type)
            event.college = request.user.college
        else:
            event = Event.objects.get(pk=body['event_id'])
            event.updated_at = timezone.now()
            if request.user.user_type.name == 'Career Service':
                event.user_types.clear()
                user_types = body['user_types'].split(',')
                for type in user_types:
                    user_type = UserType.objects.get(pk=type)
                    event.user_types.add(user_type)

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
        if 'location_title' in body:
            event.location_title = body['location_title']
        if 'location_address' in body:
            event.location_address = body['location_address']
        if 'event_date_start' in body:
            event.event_date_start = body['event_date_start']
        if 'event_date_end' in body:
            event.event_date_end = body['event_date_end']
        if 'event_type_id' in body:
            event.event_type = EventType.objects.get(pk=int(body['event_type_id']))
        if 'spot_count' in body:
            event.spot_count = int(body['spot_count'])
        if 'header_image' in body:
            file = body['header_image']
            ext = file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)
            event.header_image.save(filename, file, save=True)
        if 'is_publish' in body:
            event.is_publish = get_boolean_from_request(request, 'is_publish', 'POST')
        if request.user.user_type.name == 'Career Service':
            event.is_approved = True
        else:
            if event.is_publish:
                send_notification_email_to_admins('event', event.college.id)
            event.is_approved = False
        event.save()
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


@csrf_exempt
@api_view(["GET"])
def stats(request):
    if request.user.user_type.name == 'Career Service':
        days = request.GET.get('days', '30')
        response = {}
        user_types = UserType.objects.filter(Q(name='Career Service') | Q(name='Student') | Q(name='Alumni')).order_by('id')
        for user_type in user_types:
            item = {}
            last_x_days_created_count = Event.objects.filter(Q(is_publish=True, is_rejected=False, is_approved=True) | Q(host_user=request.user),
                                                host_user__user_type__id=int(user_type.id), college=request.user.college,
                                                             created_at__lte=datetime.datetime.today(),
                                       created_at__gt=datetime.datetime.today() - datetime.timedelta(days=int(days))).count()
            upcoming_x_days_count = Event.objects.filter(Q(is_publish=True, is_rejected=False, is_approved=True) | Q(host_user=request.user),
                                                host_user__user_type__id=int(user_type.id), college=request.user.college,
                                                         event_date_start__gte=datetime.datetime.today(),
                                                             created_at__lt=datetime.datetime.today() + datetime.timedelta(
                                                                 days=int(days))).count()
            item['last_x_days_created'] = last_x_days_created_count
            item['upcoming_x_days'] = upcoming_x_days_count
            response[user_type.name] = item
        return JsonResponse(create_response(data=response), safe=False)
    return JsonResponse(
        create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
        safe=False)