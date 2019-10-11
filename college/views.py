from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from utils.error_codes import ResponseCodes

from JH_RestAPI import pagination
from utils.generic_json_creator import create_response
from .models import College, CollegeCoach, HomePage, HomePageVideo
from .serializers import CollegeSerializer, CollegeCoachSerializer, HomePageSerializer, HomePageVideoSerializer


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
@api_view(["GET"])
def coaches(request):
    if not request.user.user_type.coach_listing_enabled:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)
    college_coaches = CollegeCoach.objects.filter(college=request.user.college, is_publish=True)
    paginator = pagination.CustomPagination()
    college_coaches = paginator.paginate_queryset(college_coaches, request)
    serialized_college_coaches = CollegeCoachSerializer(
        instance=college_coaches, many=True).data
    return JsonResponse(create_response(data=serialized_college_coaches, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET"])
def home_page_videos(request):
    homepage_videos = HomePageVideo.objects.filter(college=request.user.college, is_publish=True)
    paginator = pagination.CustomPagination()
    homepage_videos = paginator.paginate_queryset(homepage_videos, request)
    serialized_homepage_videos = HomePageVideoSerializer(
        instance=homepage_videos, many=True).data
    return JsonResponse(create_response(data=serialized_homepage_videos, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET"])
def home_page(request):
    user_profile = request.user
    if user_profile.user_type.name == 'Alumni' or user_profile.user_type.name == 'Career Service':
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
    else:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)