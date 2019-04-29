from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from django.http import JsonResponse
from .models import Company
from position.models import JobPosition
from jobapps.models import JobApplication
from .serializers import CompanySerializer
from position.serializers import JobPositionSerializer
from JH_RestAPI import pagination


@csrf_exempt
@api_view(["GET"])
def get_companies(request):
    companies = Company.objects.all()
    paginator = pagination.CustomPagination()
    companies = paginator.paginate_queryset(companies, request)
    serialized_companies = CompanySerializer(instance=companies, many=True, context={'user':request.user}).data
    return JsonResponse(create_response(data=serialized_companies, paginator=paginator), safe=False) 

@csrf_exempt
@api_view(["GET"])
def get_company_positions(request, company_pk):
    company = Company.objects.get(pk=company_pk)
    queryset = JobApplication.objects.filter(companyObject=company)
    positions = set()
    for q in queryset:
        positions.add(q.position)
    return JsonResponse(create_response(data=JobPositionSerializer(instance=positions, many=True).data), safe=False)

