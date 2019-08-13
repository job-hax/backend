from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from jobapps.models import JobApplication
from position.serializers import JobPositionSerializer
from utils.generic_json_creator import create_response
from .models import Company
from review.models import Review
from .serializers import CompanySerializer


@csrf_exempt
@api_view(["GET"])
def companies(request):
    q = request.GET.get('q')
    has_review = request.GET.get('hasReview')
    mine = request.GET.get('mine')
    companies = Company.objects.all()
    if has_review is not None:
        companies_has_review = Review.objects.order_by('company__id').distinct('company__id')
        companies = Company.objects.all().filter(id__in=[r.company.id for r in companies_has_review])
    if mine is not None:
        users_companies = JobApplication.objects.filter(user=request.user, isDeleted=False)
        companies = companies.filter(id__in=[j.companyObject.id for j in users_companies])
    if q is not None:
        companies = companies.filter(company__icontains=q)
    paginator = pagination.CustomPagination()
    companies = paginator.paginate_queryset(companies, request)
    serialized_companies = CompanySerializer(
        instance=companies, many=True, context={'user': request.user}).data
    return JsonResponse(create_response(data=serialized_companies, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET"])
def positions(request, company_pk):
    has_review = request.GET.get('hasReview')
    company = Company.objects.get(pk=company_pk)
    queryset = JobApplication.objects.filter(companyObject=company)
    if has_review is not None:
        positions_has_review = Review.objects.filter(company=company).order_by('position__id').distinct('position__id')
        queryset = queryset.filter(position__id__in=[r.position.id for r in positions_has_review])
    positions = set()
    for q in queryset:
        if q is not None:
            positions.add(q.position)
    return JsonResponse(create_response(data=JobPositionSerializer(instance=positions, many=True).data), safe=False)
