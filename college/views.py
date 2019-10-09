from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from utils.generic_json_creator import create_response
from .models import College
from .serializers import CollegeSerializer


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
