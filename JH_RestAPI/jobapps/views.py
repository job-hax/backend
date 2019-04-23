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
from .models import StatusHistory
from .models import JobApplicationNote
from position.models import JobPosition
from company.models import Company
from utils.clearbit_company_checker import get_company_detail
from .serializers import JobApplicationSerializer
from .serializers import ApplicationStatusSerializer
from .serializers import JobAppllicationDetailSerializer
from .serializers import StatusHistorySerializer
from .serializers import JobApplicationNoteSerializer
import json
from utils.logger import log
from rest_framework.parsers import JSONParser
from datetime import datetime   


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
@api_view(["GET"])
def get_status_history(request):
    jobapp_id = request.GET.get('jopapp_id')
    success = True
    code = 0
    slist = []  
    if jobapp_id is None:
        success = False
        code = 10
    else:    
        statuses = StatusHistory.objects.filter(job_post__pk = jobapp_id)
        try:
            slist = StatusHistorySerializer(instance=statuses, many=True).data
        except Exception as e:
            log(e, 'e')  
            success=False
            code=11     
    return JsonResponse(create_response(slist, success, code), safe=False)   

@csrf_exempt
@api_view(["GET"])
def get_jobapp_notes(request):
    jobapp_id = request.GET.get('jopapp_id')
    success = True
    code = 0
    slist = []  
    if jobapp_id is None:
        success = False
        code = 10
    else:    
        notes = JobApplicationNote.objects.filter(job_post__pk = jobapp_id)
        try:
            slist = JobApplicationNoteSerializer(instance=notes, many=True).data
        except Exception as e:
            log(e, 'e')  
            success=False
            code=11     
    return JsonResponse(create_response(slist, success, code), safe=False) 

@csrf_exempt
@api_view(["POST"])
def update_jobapp_note(request):
    body = request.data
    jobapp_note_id = body['jobapp_note_id']
    description = body['description']
    success = True
    code = 0
    if jobapp_note_id is None:
        success = False
        code = 10
    else:    
        try:
            note = JobApplicationNote.objects.get(pk = jobapp_note_id)
            note.description = description
            note.update_date = datetime.now()
            note.save()
        except Exception as e:
            log(e, 'e')  
            success=False
            code=11     
    return JsonResponse(create_response(None, success, code), safe=False)     

@csrf_exempt
@api_view(["POST"])
def delete_jobapp_note(request):
    body = request.data
    jobapp_note_id = body['jobapp_note_id']
    success = True
    code = 0
    if jobapp_note_id is None:
        success = False
        code = 10
    else:
        user_job_app_note = JobApplicationNote.objects.filter(pk=jobapp_note_id)
        if len(user_job_app_note) == 0:
            success = False
            code = 11
        else:
            user_job_app_note = user_job_app_note[0]
            user_job_app_note.delete()
    return JsonResponse(create_response(None, success, code), safe=False)    

@csrf_exempt
@api_view(["POST"])
def add_jobapp_note(request):
    body = request.data
    jobapp_id = body['jobapp_id']
    description = body['description']
    success = True
    code = 0
    data = None
    if jobapp_id is None or description is None:
        success = False
        code = 10
    else:    
        try:
            user_job_app = JobApplication.objects.get(pk=jobapp_id)
            note = JobApplicationNote(job_post = user_job_app, description=description)
            note.save()
            data = JobApplicationNoteSerializer(instance=note, many=False).data
        except Exception as e:
            log(e, 'e')  
            success=False
            code=11     
    return JsonResponse(create_response(data, success, code), safe=False)     

@csrf_exempt
@api_view(["POST"])
def update_jobapp(request):
    body = request.data
    status_id = body.get('status_id')
    rejected = body.get('rejected')
    jobapp_id = body.get('jobapp_id')
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
                    status_history = StatusHistory(job_post = user_job_app, applicationStatus = new_status[0])
                    status_history.save()    
            user_job_app.save()
    return JsonResponse(create_response(None, success, code), safe=False)

@csrf_exempt
@api_view(["POST"])
def delete_jobapp(request):
    body = request.data
    jobapp_id = body['jobapp_id']
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
    body = request.data
    job_title = body['job_title']
    company = body['company']
    applicationdate = body['application_date']
    status = int(body['status_id'])
    source = body['source']
    #jt is current dummy job title in the db
    jt = JobPosition.objects.all().filter(job_title=job_title)
    if jt is None or len(jt) == 0:
        jt = JobPosition(job_title=job_title)
        jt.save()
    else:
        jt = jt[0]  
     #check if the company details already exists in the db 
    cd = get_company_detail(company)  
    if cd is None:
        company_title = company
    else:
        company_title = cd['name'] 
    jc = Company.objects.all().filter(cb_name=company_title)
    if jc is None or len(jc) == 0:
        #if company doesnt exist save it
        if cd is None:
            jc = Company(company=company, company_logo=None, cb_name=company, cb_company_logo=None, cb_domain=None)
        else:    
            jc = Company(company=company, company_logo=None, cb_name=cd['name'], cb_company_logo=cd['logo'], cb_domain=cd['domain'])
        jc.save()      
    else:
        jc = jc[0]       
    japp = JobApplication(position=jt, companyObject=jc, applyDate=applicationdate, msgId='', source =source, user = request.user)
    japp.applicationStatus = ApplicationStatus.objects.get(pk=status)
    japp.save()
    return JsonResponse(create_response(JobApplicationSerializer(instance=japp, many=False).data), safe=False)


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
    log(e, 'e')  
    success=False
    code=11
    jobapp_detail=None
  return JsonResponse(create_response(jobapp_detail,success,code), safe=False)
