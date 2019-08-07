from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from users.models import Profile
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from .serializers import AlumniSerializer


@csrf_exempt
@api_view(["GET"])
def alumni(request):
    user_profile = Profile.objects.get(user=request.user)
    if user_profile.user_type < int(Profile.UserTypes.student):
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user), safe=False)
    alumni_list = Profile.objects.filter(user_type=int(Profile.UserTypes.alumni), college__pk=user_profile.college.id)

    q = request.GET.get('q')
    year = request.GET.get('year')
    major_id = request.GET.get('major_id')
    country_id = request.GET.get('country_id')
    state_id = request.GET.get('state_id')
    if q is not None and len(q) > 3:
        alumni_list = alumni_list.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
    if year is not None:
        alumni_list = alumni_list.filter(grad_year__gte=year)
    if major_id is not None:
        alumni_list = alumni_list.filter(major__pk=major_id)
    if country_id is not None:
        alumni_list = alumni_list.filter(country__pk=country_id)
    if state_id is not None:
        alumni_list = alumni_list.filter(state__pk=state_id)

    paginator = pagination.CustomPagination()
    alumni_list = paginator.paginate_queryset(alumni_list, request)
    serialized_alumni = AlumniSerializer(
        instance=alumni_list, many=True, context={'user': request.user}).data
    return JsonResponse(create_response(data=serialized_alumni, paginator=paginator), safe=False)

