from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
from utils.generic_json_creator import create_response
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from utils.gmail_lookup import fetchJobApplications
from background_task import background

# Create your views here.
@require_POST
@csrf_exempt
def auth_social_user(request):
    post_data = {'client_id': request.POST['client_id']}
    post_data['client_secret'] = request.POST['client_secret']
    post_data['grant_type'] = 'convert_token'
    provider = request.POST['provider']
    post_data['backend'] = provider
    post_data['token'] = request.POST['token']
    response = requests.post('http://localhost:8000/auth/convert-token', data=post_data)
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = 1
    else:
        success = True   
        code = 0 
    return JsonResponse(create_response(jsonres, success, code), safe=False)

@csrf_exempt
@api_view(["GET"])
def sync_user_emails(request):
    #it'll be used for background tasking in production
    #refs. https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e
    #https://django-background-tasks.readthedocs.io/en/latest/
    #https://stackoverflow.com/questions/41205607/how-to-activate-the-process-queue-in-django-background-tasks
    #scheduleFetcher.now(request.user.id)
    scheduleFetcher(request.user.id)
    return JsonResponse(create_response(None), safe=False)

@background(schedule=1)
def scheduleFetcher(user_id):
    user = User.objects.get(pk=user_id)
    if user.social_auth.filter(provider='google-oauth2'):
        fetchJobApplications(user)    
