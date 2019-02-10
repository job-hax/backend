from django.shortcuts import render
from django.http import JsonResponse
from jobapps.models import JobApplication
from jobapps.models import ApplicationStatus
from users.models import Profile
from jobapps.models import JobPostDetail
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.db.models import Count
from utils.generic_json_creator import create_response

@csrf_exempt
@api_view(["GET"])
def get_total_application_count(request):
  count = JobApplication.objects.filter(user_id=request.user.id).count()
  response = {}
  response['count'] = count
  return JsonResponse(create_response(response), safe=False)

@csrf_exempt
@api_view(["GET"])
def get_application_count_by_month(request):
  response = []
  sources = ['Hired.com','LinkedIn','Indeed','Vettery', 'Others']
  for i in sources:
    if i != 'Others':
      appsByMonths = JobApplication.objects.filter(user_id=request.user.id,source=i,applyDate__year='2018').values('applyDate__year', 'applyDate__month').annotate(count=Count('pk'))
    else:  
      appsByMonths = JobApplication.objects.filter(~Q(source = 'LinkedIn'),~Q(source = 'Hired.com'),~Q(source = 'Indeed'),~Q(source = 'Vettery'),user_id=request.user.id,applyDate__year='2018').values('applyDate__year', 'applyDate__month').annotate(count=Count('pk'))
    item = {}
    item['source'] = i
    data = [0] * 12
    for app in appsByMonths:
      data[app['applyDate__month'] - 1] = app['count']
    item['data'] = data  
    response.append(item)
  return JsonResponse(create_response(response), safe=False)

@csrf_exempt
@api_view(["GET"])
def get_application_count_by_month_with_total(request):
  response = []
  sources = ['Hired.com','LinkedIn','Indeed', 'Vettery', 'Others', 'Total']
  for i in sources:
    if i == 'Total':
      appsByMonths = JobApplication.objects.filter(user_id=request.user.id,applyDate__year='2018').values('applyDate__year', 'applyDate__month').annotate(count=Count('pk'))
    elif i != 'Others':
      appsByMonths = JobApplication.objects.filter(user_id=request.user.id,source=i,applyDate__year='2018').values('applyDate__year', 'applyDate__month').annotate(count=Count('pk'))
    else:  
      appsByMonths = JobApplication.objects.filter(~Q(source = 'LinkedIn'),~Q(source = 'Hired.com'),~Q(source = 'Indeed'),~Q(source = 'Vettery'),user_id=request.user.id,applyDate__year='2018').values('applyDate__year', 'applyDate__month').annotate(count=Count('pk'))
    item = {}
    item['source'] = i
    data = [0] * 12
    for app in appsByMonths:
      data[app['applyDate__month'] - 1] = app['count']
    item['data'] = data  
    response.append(item)
  return JsonResponse(create_response(response), safe=False)  

@csrf_exempt
@api_view(["GET"])
def get_count_by_statuses(request):
  statuses = JobApplication.objects.filter(~Q(applicationStatus = None),user_id=request.user.id).values('applicationStatus').annotate(count=Count('pk'))
  response = []
  for i in statuses:
    item = {}
    item['name'] = ApplicationStatus.objects.get(pk=i['applicationStatus']).value
    item['value'] = i['count']
    response.append(item)
  return JsonResponse(create_response(response), safe=False)
  
@csrf_exempt
@api_view(["GET"])  
def get_word_count(request):
  response = []
  companies = JobApplication.objects.filter(user_id=request.user.id).values('company').annotate(count=Count('pk'))
  for i in companies:
    item = {}
    item['word'] = i['company']
    item['value'] = i['count']
    response.append(item)  
  return JsonResponse(create_response(response), safe=False)  

@csrf_exempt
@api_view(["GET"])
def get_count_by_jobtitle_and_statuses(request):
  response = {}
  job_titles = JobApplication.objects.filter(~Q(applicationStatus = None),user_id=request.user.id).values('jobTitle').annotate(count=Count('pk'))
  jobs = []
  statuses_data = []
  status_data = []
  for job_title in job_titles:
    jobs.append(job_title['jobTitle'])
  response['jobs'] = jobs
  statuses = ApplicationStatus.objects.all()
  for status in statuses:
    statuses_data.append(status.value)
    item = {}
    item['name'] = status.value
    data = [0] * len(job_titles)
    for i,job_title in enumerate(job_titles):
      data[i] = JobApplication.objects.filter(user_id=request.user.id, jobTitle=job_title['jobTitle'], applicationStatus=status).count()
    item['data'] = data
    status_data.append(item)
  response['statuses'] = statuses_data  
  response['data'] = status_data  
  return JsonResponse(create_response(response), safe=False)
