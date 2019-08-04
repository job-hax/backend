from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from django.http import JsonResponse
from .models import College, Major
from .serializers import CollegeSerializer, MajorSerializer
from JH_RestAPI import pagination


@csrf_exempt
@api_view(["GET"])
def get_colleges(request):
    q = request.GET.get('q')
    if q is None:
        colleges = College.objects.all()
    else:
        colleges = College.objects.filter(name__icontains=q)
    paginator = pagination.CustomPagination()
    colleges = paginator.paginate_queryset(colleges, request)
    serialized_colleges = CollegeSerializer(
        instance=colleges, many=True,).data
    return JsonResponse(create_response(data=serialized_colleges, paginator=paginator), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_majors(request):
    q = request.GET.get('q')
    if q is None:
        majores = Major.objects.all()
    else:
        majores = Major.objects.filter(name__icontains=q)
    paginator = pagination.CustomPagination()
    majores = paginator.paginate_queryset(majores, request)
    serialized_majores = MajorSerializer(
        instance=majores, many=True,).data
    return JsonResponse(create_response(data=serialized_majores, paginator=paginator), safe=False)