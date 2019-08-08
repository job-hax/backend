from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from utils.generic_json_creator import create_response
from .models import JobPosition
from .serializers import JobPositionSerializer


@csrf_exempt
@api_view(["GET"])
def positions(request):
    q = request.GET.get('q')
    if q is None:
        positions = JobPosition.objects.all()
    else:
        positions = JobPosition.objects.filter(job_title__icontains=q)
    if request.GET.get('count') is not None:
        cnt = int(request.GET.get('count'))
        positions = positions[:cnt]
    serialized_positions = JobPositionSerializer(
        instance=positions, many=True).data
    return JsonResponse(create_response(data=serialized_positions, paginator=None), safe=False)
