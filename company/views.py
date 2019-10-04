from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from position.serializers import JobPositionSerializer
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request
from .models import Company
from .serializers import CompanySerializer


@csrf_exempt
@api_view(["GET"])
def companies(request):
    q = request.GET.get('q')
    companies = Company.objects.all()
    if q is not None:
        companies = companies.filter(company__icontains=q)
    paginator = pagination.CustomPagination()
    companies = paginator.paginate_queryset(companies, request)
    serialized_companies = CompanySerializer(
        instance=companies, many=True, context={'user': request.user}).data
    return JsonResponse(create_response(data=serialized_companies, paginator=paginator), safe=False)
