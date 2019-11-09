from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from utils.generic_json_creator import create_response
from .models import JobPosition, PositionDetail
from .serializers import JobPositionSerializer, PositionDetailSerializer
from utils.models import Country, State
from company.utils import get_or_create_company
from company.models import Company


@csrf_exempt
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def positions(request):
    body = request.data
    if request.method == "GET":
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
    elif request.method == "POST":
        job_title = body["job_title"]
        responsibilities = body["responsibilities"]
        requirements = body["requirements"]
        department = body["department"]
        job_type = body["job_type"]
        city = body["city"]
        company_id = int(body["company_id"])
        job = JobPosition.objects.get(job_title=job_title)
        state = State.objects.get(pk=body["state_id"])
        country = Country.objects.get(pk=body["country_id"])
        company = Company.objects.get(pk=body["company_id"])

        new_position = PositionDetail(job=job, responsibilities=responsibilities, requirements=requirements,
                                      department=department, job_type=job_type, city=city, country=country, state=state, company=company)
        new_position.save()
        return JsonResponse(
            create_response(
                data=PositionDetailSerializer(instance=new_position, many=False, context={'user': request.user}).data),
            safe=False)
    elif request.method == "DELETE":
        position_id = body["position_id"]
        position = PositionDetail.objects.get(pk=position_id)
        position.is_deleted = True
        position.save()
        return JsonResponse(create_response(data=None), safe=False)
