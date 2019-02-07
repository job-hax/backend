from django.shortcuts import render
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.db import models
from .models import JobApplication
from .models import JobPostDetail
from .models import ApplicationStatus
from .serializers import JobApplicationSerializer
from .serializers import ApplicationStatusSerializer
from .serializers import JobAppllicationDetailSerializer
import json

# Create your views here.
@csrf_exempt
@api_view(["GET"])
def get_jobapps(request):
    status_id = request.GET.get('status_id')
    if status_id is not None:
        user_job_apps = JobApplication.objects.filter(applicationStatus_id=status_id,user_id=request.user.id, isDeleted=False).order_by('-applyDate')
    else:
        user_job_apps = JobApplication.objects.filter(user_id=request.user.id, isDeleted=False).order_by('-applyDate')
    joblist = JobApplicationSerializer(instance=user_job_apps, many=True).data
    return JsonResponse(create_response(joblist), safe=False)

@csrf_exempt
@api_view(["GET"])
def get_statuses(request):
    statuses = ApplicationStatus.objects.all()
    slist = ApplicationStatusSerializer(instance=statuses, many=True).data
    return JsonResponse(create_response(slist), safe=False)

@csrf_exempt
@api_view(["POST"])
def update_jobapp(request):
    status_id = request.POST.get('status_id')
    rejected = get_boolean_from_request(request, 'rejected', 'POST')
    jobapp_id = request.POST.get('jobapp_id')
    success = True
    code = 0
    if jobapp_id is None:
        success = False
        code = 10
    elif rejected is None and status_id is None:
        success = False
        code = 10
    else:
        user_job_app = JobApplication.objects.filter(pk=jobapp_id)
        if len(user_job_app) == 0:
            success = False
            code = 11
        else:
            user_job_app = user_job_app[0]
            if status_id is None:
                user_job_app.isRejected = rejected
            else:
                new_status = ApplicationStatus.objects.filter(pk=status_id)
                if len(new_status) == 0:
                    success = False
                    code = 11
                else:
                    if rejected is None:
                        user_job_app.applicationStatus = new_status[0]
                    else:
                        user_job_app.applicationStatus = new_status[0]
                        user_job_app.isRejected = rejected
            user_job_app.save()
    return JsonResponse(create_response(None, success, code), safe=False)

@csrf_exempt
@api_view(["POST"])
def delete_jobapp(request):
    jobapp_id = request.POST.get('jobapp_id')
    success = True
    code = 0
    if jobapp_id is None:
        success = False
        code = 10
    else:
        user_job_app = JobApplication.objects.filter(pk=jobapp_id)
        if len(user_job_app) == 0:
            success = False
            code = 11
        else:
            user_job_app = user_job_app[0]
            user_job_app.isDeleted = True
            user_job_app.save()
    return JsonResponse(create_response(None, success, code), safe=False)

@csrf_exempt
@api_view(["POST"])
def add_jobapp(request):
    job_title = request.POST['job_title']
    company = request.POST['company']
    applicationdate = request.POST['application_date']
    status = int(request.POST['status_id'])
    source = request.POST['source']

    japp = JobApplication(jobTitle=job_title, company=company, applyDate=applicationdate, msgId='', source =source, user = request.user, companyLogo = None)
    japp.applicationStatus = ApplicationStatus.objects.get(pk=status)
    japp.save()
    return JsonResponse(create_response(None), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_jobapp_detail(request):
  id = request.GET.get('jopapp_id')
  try:
    details = JobPostDetail.objects.all().get(job_post__pk = id)
    jobapp_detail = {}
    jobapp_detail['posterInformation'] = json.loads(details.posterInformation)
    jobapp_detail['decoratedJobPosting'] = json.loads(details.decoratedJobPosting)
    jobapp_detail['topCardV2'] = json.loads(details.topCardV2)
    success=True
    code=0 
  except Exception as e:
    print(e)  
    success=False
    code=11
    jobapp_detail=None
  return JsonResponse(create_response(jobapp_detail,success,code), safe=False)
