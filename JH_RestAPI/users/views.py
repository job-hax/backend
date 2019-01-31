from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
from utils.generic_json_creator import create_response
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .models import Profile
from jobapps.models import GoogleMail
from jobapps.serializers import GoogleMailSerializer
from utils.gmail_lookup import fetchJobApplications
from background_task import background
from social_django.models import UserSocialAuth


# Create your views here.
@require_POST
@csrf_exempt
def register(request):
    # Get form values
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']

    success = True
    code = 0

    # Check if passwords match
    if password == password2:
        # Check username
        if User.objects.filter(username=username).exists():
            success = False
            code = 8
        else:
            if User.objects.filter(email=email).exists():
                success = False
                code = 9
            else:
                # Looks good
                user = User.objects.create_user(username=username, password=password,email=email, first_name=first_name, last_name=last_name)
                user.save()
    else:
        success = False
        code = 7
    return JsonResponse(create_response(None, success, code), safe=False)    

@require_POST
@csrf_exempt
def login(request):
    post_data = {'client_id': request.POST['client_id']}
    post_data['client_secret'] = request.POST['client_secret']
    post_data['grant_type'] = 'password'
    post_data['username'] = request.POST['username']
    post_data['password'] = request.POST['password']
    response = requests.post('http://localhost:8000/auth/token', data=post_data)
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = 6
    else:
        success = True   
        code = 0 
    return JsonResponse(create_response(jsonres, success, code), safe=False)

@require_POST
@csrf_exempt
def logout(request):
    post_data = {'client_id': request.POST['client_id']}
    headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION')}
    response = requests.post('http://localhost:8000/auth/invalidate-sessions', data=post_data, headers=headers)
    if response.status_code is 204 or response.status_code is 200:
        success = True
        code = 0
    else:
        success = False   
        code = 5 
    return JsonResponse(create_response(None, success, code), safe=False)


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

@require_POST
@csrf_exempt
def refresh_token(request):
    post_data = {'client_id': request.POST['client_id']}
    post_data['client_secret'] = request.POST['client_secret']
    post_data['grant_type'] = 'refresh_token'
    post_data['refresh_token'] = request.POST['refresh_token']
    response = requests.post('http://localhost:8000/auth/token', data=post_data)
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
    profile = Profile.objects.get(user=request.user)
    if not profile.is_gmail_read_ok:
        return JsonResponse(create_response(None, False, 4), safe=False)    
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

@require_POST
@csrf_exempt
@api_view(["POST"])
def update_gmail_token(request):
    token = request.POST['token']
    try:
        user_profile = UserSocialAuth.objects.get(user=request.user)
        print(user_profile)
        if user_profile is not None:
            user_profile.extra_data['access_token'] = token
            user_profile.save()
            success = True
            code = 0
            scheduleFetcher(request.user.id)
        else:
            success = False
            code = 2
    except Exception as e: 
        print(e)
        success = False   
        code = 3         
    return JsonResponse(create_response(None, success, code), safe=False)    

@csrf_exempt
@api_view(["GET"])
def get_user_google_mails(request):
    mails = GoogleMail.objects.all()
    slist = GoogleMailSerializer(instance=mails, many=True).data
    return JsonResponse(create_response(slist), safe=False)    
