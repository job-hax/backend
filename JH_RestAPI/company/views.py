from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from jobapps.models import JobApplication
from position.serializers import JobPositionSerializer
from utils.generic_json_creator import create_response
from .models import Company
from .serializers import CompanySerializer


@csrf_exempt
@api_view(["GET"])
def companies(request):
    q = request.GET.get('q')
    if q is None:
        companies = Company.objects.all()
    else:
        companies = Company.objects.filter(company__icontains=q)
    paginator = pagination.CustomPagination()
    companies = paginator.paginate_queryset(companies, request)
    serialized_companies = CompanySerializer(
        instance=companies, many=True, context={'user': request.user}).data
    return JsonResponse(create_response(data=serialized_companies, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET"])
def positions(request, company_pk):
    company = Company.objects.get(pk=company_pk)
    queryset = JobApplication.objects.filter(companyObject=company)
    positions = set()
    for q in queryset:
        positions.add(q.position)
    return JsonResponse(create_response(data=JobPositionSerializer(instance=positions, many=True).data), safe=False)
