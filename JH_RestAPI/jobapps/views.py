from django.shortcuts import render
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.db import models
from .models import JobApplication
from .models import ApplicationStatus
from .serializers import JobApplicationSerializer
from .serializers import ApplicationStatusSerializer

# Create your views here.
@csrf_exempt
@api_view(["GET"])
def get_jobapps(request):
    user_job_apps = JobApplication.objects.filter(user_id=request.user.id).order_by('-applyDate')
    joblist = JobApplicationSerializer(instance=user_job_apps, many=True).data
    return JsonResponse(create_response(joblist), safe=False)

@csrf_exempt
@api_view(["GET"])
def get_statuses(request):
    statuses = ApplicationStatus.objects.all()
    slist = ApplicationStatusSerializer(instance=statuses, many=True).data
    return JsonResponse(create_response(slist), safe=False)    