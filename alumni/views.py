from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from utils.generic_json_creator import create_response
from .serializers import AlumniSerializer
from major.serializers import MajorSerializer
from company.serializers import CompanyBasicsSerializer
from college.models import College
from utils.error_codes import ResponseCodes
from position.serializers import JobPositionSerializer

User = get_user_model()


@csrf_exempt
@api_view(["GET"])
def alumni(request):
    user_profile = request.user
    if not user_profile.user_type.alumni_listing_enabled:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)
    alumni_list = User.objects.filter(user_type__name__iexact='Alumni', college__pk=user_profile.college.id, is_demo=False)

    q = request.GET.get('q')
    year = request.GET.get('year')
    major_id = request.GET.get('major_id')
    company_id = request.GET.get('company_id')
    position_id = request.GET.get('position_id')
    country_id = request.GET.get('country_id')
    state_id = request.GET.get('state_id')
    if q is not None:
        alumni_list = alumni_list.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))
    if year is not None:
        alumni_list = alumni_list.filter(grad_year=year)
    if major_id is not None:
        alumni_list = alumni_list.filter(major__pk=major_id)
    if company_id is not None:
        alumni_list = alumni_list.filter(company__pk=company_id)
    if position_id is not None:
        alumni_list = alumni_list.filter(job_position__pk=position_id)
    if country_id is not None:
        alumni_list = alumni_list.filter(country__pk=country_id)
    if state_id is not None:
        alumni_list = alumni_list.filter(state__pk=state_id)

    paginator = pagination.CustomPagination()
    alumni_list = paginator.paginate_queryset(alumni_list, request)
    serialized_alumni = AlumniSerializer(
        instance=alumni_list, many=True, context={'user': request.user}).data
    return JsonResponse(create_response(data=serialized_alumni, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET"])
def majors(request):
    user_profile = request.user
    if not user_profile.user_type.alumni_listing_enabled:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)
    college = College.objects.get(pk=user_profile.college.pk)
    alumni = User.objects.filter(~Q(major=None), college=college, user_type__name__iexact='Alumni', is_demo=False)
    data = []
    for a in alumni:
        if a.major is not None:
            data.append(a.major)
    data = set(data)
    serialized_majors = MajorSerializer(
        instance=data, many=True, ).data
    return JsonResponse(create_response(data=serialized_majors), safe=False)


@csrf_exempt
@api_view(["GET"])
def companies(request):
    user_profile = request.user
    if not user_profile.user_type.alumni_listing_enabled:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)
    college = College.objects.get(pk=user_profile.college.pk)
    alumni = User.objects.filter(~Q(major=None), college=college, user_type__name__iexact='Alumni', is_demo=False)
    data = []
    for a in alumni:
        if a.company is not None:
            data.append(a.company)
    data = set(data)
    serialized_companies = CompanyBasicsSerializer(
        instance=data, many=True, ).data
    return JsonResponse(create_response(data=serialized_companies), safe=False)


@csrf_exempt
@api_view(["GET"])
def positions(request):
    user_profile = request.user
    if not user_profile.user_type.alumni_listing_enabled:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)
    college = College.objects.get(pk=user_profile.college.pk)
    alumni = User.objects.filter(~Q(major=None), college=college, user_type__name__iexact='Alumni', is_demo=False)
    data = []
    for a in alumni:
        if a.job_position is not None:
            data.append(a.job_position)
    data = set(data)
    serialized_positions = JobPositionSerializer(
        instance=data, many=True, ).data
    return JsonResponse(create_response(data=serialized_positions), safe=False)