from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from utils.error_codes import ResponseCodes
import uuid
import json
from JH_RestAPI import pagination
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request
from .models import College, CollegeCoach, HomePage, HomePageVideo, LandingPage
from .serializers import CollegeSerializer, CollegeCoachSerializer, HomePageSerializer, HomePageVideoSerializer, LandingPageSerializer
import os
from django.core.files.storage import default_storage
from django.conf import settings


@csrf_exempt
@api_view(["GET"])
def colleges(request):
    q = request.GET.get('q')
    if q is None:
        colleges = College.objects.all()
    else:
        colleges = College.objects.filter(short_name__icontains=q)
        if colleges.count() == 0:
            colleges = College.objects.filter(Q(name__icontains=q) | Q(short_name__icontains=q))
    paginator = pagination.CustomPagination()
    colleges = paginator.paginate_queryset(colleges, request)
    serialized_colleges = CollegeSerializer(
        instance=colleges, many=True, ).data
    return JsonResponse(create_response(data=serialized_colleges, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET", "POST", "PUT", "DELETE"])
def coaches(request):
    user_profile = request.user
    body = request.data
    if request.method == "GET":
        if not request.user.user_type.coach_listing_enabled:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                                safe=False)
        college_coaches = CollegeCoach.objects.filter(college=request.user.college)
        paginator = pagination.CustomPagination()
        college_coaches = paginator.paginate_queryset(college_coaches, request)
        serialized_college_coaches = CollegeCoachSerializer(
            instance=college_coaches, many=True).data
        return JsonResponse(create_response(data=serialized_college_coaches, paginator=paginator), safe=False)
    elif user_profile.user_type.name == 'Career Service':
        if request.method == "DELETE":
            coach = HomePageVideo.objects.get(pk=body['coach_id'])
            coach.delete()
            return JsonResponse(create_response(data=None), safe=False)
        elif request.method == "POST" and user_profile.user_type.name == 'Career Service':
            coach = CollegeCoach()
            coach.first_name = body['first_name']
            coach.last_name = body['last_name']
            coach.title = body['title']
            if 'email' in body:
                coach.email = body['email']
            coach.content = body['content']
            coach.calendar_link = body['calendar_link']
            if 'online_conference_link' in body:
                coach.online_conference_link = body['online_conference_link']
            coach.college = user_profile.college

            if 'is_publish' in body:
                coach.is_publish = get_boolean_from_request(request, 'is_publish', 'POST')
            else:
                coach.is_publish = True

            file = body['profile_photo']
            ext = file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)
            coach.profile_photo.save(filename, file, save=True)

            file = body['summary_photo']
            ext = file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)
            coach.summary_photo.save(filename, file, save=True)

            coach.save()
            return JsonResponse(create_response(data=CollegeCoachSerializer(
                instance=coach, many=False).data), safe=False)
        elif request.method == "PUT" and user_profile.user_type.name == 'Career Service':
            coach = CollegeCoach.objects.get(pk=body['coach_id'])
            if 'first_name' in body:
                coach.first_name = body['first_name']
            if 'last_name' in body:
                coach.last_name = body['last_name']
            if 'title' in body:
                coach.title = body['title']
            if 'email' in body:
                coach.email = body['email']
            if 'content' in body:
                coach.content = body['content']
            if 'calendar_link' in body:
                coach.calendar_link = body['calendar_link']
            if 'online_conference_link' in body:
                coach.online_conference_link = body['online_conference_link']
            if 'profile_photo' in body:
                file = body['profile_photo']
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                coach.profile_photo.save(filename, file, save=True)
            if 'summary_photo' in body:
                file = body['summary_photo']
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                coach.summary_photo.save(filename, file, save=True)
            if 'is_publish' in body:
                coach.is_publish = get_boolean_from_request(request, 'is_publish', 'POST')
            coach.save()
            return JsonResponse(create_response(data=CollegeCoachSerializer(
                instance=coach, many=False).data), safe=False)
    return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                        safe=False)


@csrf_exempt
@api_view(["GET", "POST", "PUT", "DELETE"])
def home_page_videos(request):
    user_profile = request.user
    if user_profile.user_type.name == 'Career Service':
        body = request.data
        if request.method == "GET":
            homepage_videos = HomePageVideo.objects.filter(college=request.user.college)
            paginator = pagination.CustomPagination()
            homepage_videos = paginator.paginate_queryset(homepage_videos, request)
            serialized_homepage_videos = HomePageVideoSerializer(
                instance=homepage_videos, many=True).data
            return JsonResponse(create_response(data=serialized_homepage_videos, paginator=paginator), safe=False)
        elif request.method == "DELETE" and user_profile.user_type.name == 'Career Service':
            home_page_video = HomePageVideo.objects.get(pk=body['homepage_video_id'])
            home_page_video.delete()
            return JsonResponse(create_response(data=None), safe=False)
        elif request.method == "POST" and user_profile.user_type.name == 'Career Service':
            home_page_video = HomePageVideo()
            if 'is_publish' in body:
                home_page_video.is_publish = body['is_publish']
            else:
                home_page_video.is_publish = True
            home_page_video.embed_code = body['embed_code']
            if 'title' in body:
                home_page_video.title = body['title']
            if 'description' in body:
                home_page_video.description = body['description']
            home_page_video.college = user_profile.college
            home_page_video.save()
            return JsonResponse(create_response(data=HomePageVideoSerializer(
                instance=home_page_video, many=False).data), safe=False)
        elif request.method == "PUT" and user_profile.user_type.name == 'Career Service':
            home_page_video = HomePageVideo.objects.get(pk=body['homepage_video_id'])
            if 'embed_code' in body:
                home_page_video.embed_code = body['embed_code']
            if 'title' in body:
                home_page_video.title = body['title']
            if 'description' in body:
                home_page_video.description = body['description']
            if 'is_publish' in body:
                home_page_video.is_publish = body['is_publish']
            home_page_video.save()
            return JsonResponse(create_response(data=HomePageVideoSerializer(
                instance=home_page_video, many=False).data), safe=False)
    return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                        safe=False)

@csrf_exempt
@api_view(["GET", "POST", "PUT", "DELETE"])
def home_page(request):
    user_profile = request.user
    if user_profile.user_type.name == 'Alumni' or user_profile.user_type.name == 'Career Service':
        body = request.data
        if 'type' in body:
            type = body['type']
        if request.method == "GET":
            if HomePage.objects.filter(college=user_profile.college).exists():
                home_page = HomePage.objects.get(college=user_profile.college)
            elif HomePage.objects.filter(college=None).exists():
                home_page = HomePage.objects.get(college=None)
            else:
                return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                                    safe=False)
            serialized_home_page = HomePageSerializer(
                instance=home_page, many=False, ).data
            return JsonResponse(create_response(data=serialized_home_page), safe=False)
        elif request.method == "DELETE" and user_profile.user_type.name == 'Career Service':
            home_page = HomePage.objects.get(college=user_profile.college)
            if type == 'header_banner':
                header_banner = home_page.header_banners
                del header_banner[int(body['order'])]
                home_page.header_banners = header_banner
            elif type == 'additional_banner':
                additional_banner = home_page.additional_banners
                del additional_banner[int(body['order'])]
                home_page.additional_banners = additional_banner
            elif type == 'social_media_account':
                social_media_account = home_page.social_media_accounts
                del social_media_account[int(body['order'])]
                home_page.social_media_accounts = social_media_account
            home_page.save()
            return JsonResponse(create_response(data=None), safe=False)
        elif request.method == "POST" and user_profile.user_type.name == 'Career Service':
            home_page = HomePage.objects.get(college=user_profile.college)
            if type == 'header_banner':
                header_banner = {}
                if body['link'].startswith('http'):
                    header_banner['internal_link'] = False
                else:
                    header_banner['internal_link'] = True
                header_banner['link'] = body['link']

                file = body['image']
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                save_path = os.path.join(settings.MEDIA_ROOT, filename)
                path = default_storage.save(save_path, file)
                header_banner['image'] = settings.MEDIA_URL + filename

                header_banners = home_page.header_banners
                header_banners.append(header_banner)
                home_page.header_banners = header_banners
            elif type == 'additional_banner':
                additional_banner = {}
                if body['link'].startswith('http'):
                    additional_banner['internal_link'] = False
                else:
                    additional_banner['internal_link'] = True
                additional_banner['link'] = body['link']

                file = body['image']
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                save_path = os.path.join(settings.MEDIA_ROOT, filename)
                path = default_storage.save(save_path, file)
                additional_banner['image'] = settings.MEDIA_URL + filename

                additional_banners = home_page.additional_banners
                additional_banners.append(additional_banner)
                home_page.additional_banners = additional_banners
            elif type == 'social_media_account':
                social_media_account = {}
                social_media_account['link'] = body['link']

                file = body['image']
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                save_path = os.path.join(settings.MEDIA_ROOT, filename)
                path = default_storage.save(save_path, file)
                social_media_account['icon'] = settings.MEDIA_URL + filename

                social_media_accounts = home_page.social_media_accounts
                social_media_accounts.append(social_media_account)
                home_page.social_media_accounts = social_media_accounts
            home_page.save()
            return JsonResponse(create_response(data=HomePageSerializer(
                instance=home_page, many=False).data), safe=False)
        elif request.method == "PUT" and user_profile.user_type.name == 'Career Service':
            home_page = HomePage.objects.get(college=user_profile.college)
            if type == 'header_banner':
                header_banner = home_page.header_banners[int(body['order'])]
                if 'link' in body:
                    if body['link'].startswith('http'):
                        header_banner['internal_link'] = False
                    else:
                        header_banner['internal_link'] = True
                    header_banner['link'] = body['link']
                if 'image' in body:
                    file = body['image']
                    ext = file.name.split('.')[-1]
                    filename = "%s.%s" % (uuid.uuid4(), ext)
                    save_path = os.path.join(settings.MEDIA_ROOT, filename)
                    path = default_storage.save(save_path, file)
                    header_banner['image'] = settings.MEDIA_URL + filename

                header_banners = home_page.header_banners
                header_banners[int(body['order'])] = header_banner
                home_page.header_banners = header_banners
            elif type == 'additional_banner':
                additional_banner = home_page.additional_banners[int(body['order'])]
                if 'link' in body:
                    if body['link'].startswith('http'):
                        additional_banner['internal_link'] = False
                    else:
                        additional_banner['internal_link'] = True
                    additional_banner['link'] = body['link']
                if 'image' in body:
                    file = body['image']
                    ext = file.name.split('.')[-1]
                    filename = "%s.%s" % (uuid.uuid4(), ext)
                    save_path = os.path.join(settings.MEDIA_ROOT, filename)
                    path = default_storage.save(save_path, file)
                    additional_banner['image'] = settings.MEDIA_URL + filename

                additional_banners = home_page.additional_banners
                additional_banners[int(body['order'])] = additional_banner
                home_page.additional_banners = additional_banners
            elif type == 'social_media_account':
                social_media_account = home_page.social_media_accounts[int(body['order'])]
                if 'link' in body:
                    social_media_account['link'] = body['link']
                if 'image' in body:
                    file = body['image']
                    ext = file.name.split('.')[-1]
                    filename = "%s.%s" % (uuid.uuid4(), ext)
                    save_path = os.path.join(settings.MEDIA_ROOT, filename)
                    path = default_storage.save(save_path, file)
                    social_media_account['icon'] = settings.MEDIA_URL + filename

                social_media_accounts = home_page.social_media_accounts
                social_media_accounts[int(body['order'])] = social_media_account
                home_page.social_media_accounts = social_media_accounts
            home_page.save()
            return JsonResponse(create_response(data=HomePageSerializer(
                instance=home_page, many=False).data), safe=False)
    return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                        safe=False)


@csrf_exempt
@api_view(["POST", "PUT", "DELETE"])
def landing_page(request):
    user_profile = request.user
    body = request.data
    landing_page, new = LandingPage.objects.get_or_create(college=user_profile.college)
    if request.method == "DELETE" and user_profile.user_type.name == 'Career Service':
        fields = landing_page.fields
        del fields[int(body['order'])]
        landing_page.fields = fields
        landing_page.save()
    elif user_profile.user_type.name == 'Career Service':
        if request.method == "POST":
            field = {}
        else:
            field = landing_page.fields[int(body['order'])]

        if 'button1' in body:
            button1 = body['button1']
            field['button1'] = button1
        else:
            field['button1'] = None
        if 'button2' in body:
            button2 = body['button2']
            field['button2'] = button2
        else:
            field['button2'] = None
        if 'title' in body:
            field['title'] = body['title']
        if 'description' in body:
            field['description'] = body['description']
        if 'image' in body:
            file = body['image']
            ext = file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)
            save_path = os.path.join(settings.MEDIA_ROOT, filename)
            path = default_storage.save(save_path, file)
            field['image'] = settings.MEDIA_URL + filename

        fields = landing_page.fields
        if fields is None:
            fields = []
        fields.append(field)
        landing_page.fields = fields
        landing_page.save()
        return JsonResponse(create_response(data=LandingPageSerializer(
            instance=landing_page, many=False).data), safe=False)
    return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                        safe=False)