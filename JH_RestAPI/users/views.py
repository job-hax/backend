from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
from utils.generic_json_creator import create_response
from utils.linkedin_lookup import get_profile
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
from rest_framework.parsers import JSONParser
from utils.logger import log
from utils.error_codes import ResponseCodes


# Create your views here.
@require_POST
@csrf_exempt
def register(request):
    # Get form values
    body = JSONParser().parse(request)
    first_name = body['first_name']
    last_name = body['last_name']
    username = body['username']
    email = body['email']
    password = body['password']
    password2 = body['password2']

    success = True
    code = ResponseCodes.success

    # Check if passwords match
    if password == password2:
        # Check username
        if User.objects.filter(username=username).exists():
            success = False
            code = ResponseCodes.username_exists
        else:
            if User.objects.filter(email=email).exists():
                success = False
                code = ResponseCodes.email_exists
            else:
                # Looks good
                user = User.objects.create_user(username=username, password=password,email=email, first_name=first_name, last_name=last_name)
                user.save()
    else:
        success = False
        code = ResponseCodes.passwords_do_not_match
    return JsonResponse(create_response(None, success, code), safe=False)    

@require_POST
@csrf_exempt
def login(request):
    body = JSONParser().parse(request)
    post_data = {'client_id': body['client_id']}
    post_data['client_secret'] = body['client_secret']
    post_data['grant_type'] = 'password'
    post_data['username'] = body['username']
    post_data['password'] = body['password']
    response = requests.post('http://localhost:8000/auth/token', data=json.dumps(post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.couldnt_login
    else:
        success = True   
        code = ResponseCodes.success 
    return JsonResponse(create_response(jsonres, success, code), safe=False)

@require_POST
@csrf_exempt
def logout(request):
    body = JSONParser().parse(request)
    post_data = {'token': body['token']}
    post_data['client_id'] = body['client_id']
    post_data['client_secret'] = body['client_secret']
    headers = {'content-type': 'application/json'}
    response = requests.post('http://localhost:8000/auth/revoke-token', data=json.dumps(post_data), headers=headers)
    log(response.text, 'i')
    if response.status_code is 204 or response.status_code is 200:
        success = True
        code = ResponseCodes.success
    else:
        success = False   
        code = ResponseCodes.couldnt_logout_user 
    return JsonResponse(create_response(None, success, code), safe=False)


@require_POST
@csrf_exempt
def auth_social_user(request):
    body = JSONParser().parse(request)
    post_data = {'client_id': body['client_id']}
    post_data['client_secret'] = body['client_secret']
    post_data['grant_type'] = 'convert_token'
    provider = body['provider']
    post_data['backend'] = provider
    post_data['token'] = body['token']
    response = requests.post('http://localhost:8000/auth/convert-token', data=json.dumps(post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.invalid_credentials
    else:
        success = True   
        code = ResponseCodes.success
    return JsonResponse(create_response(jsonres, success, code), safe=False)

@require_POST
@csrf_exempt
def refresh_token(request):
    body = JSONParser().parse(request)
    post_data = {'client_id': body['client_id']}
    post_data['client_secret'] = body['client_secret']
    post_data['grant_type'] = 'refresh_token'
    post_data['refresh_token'] = body['refresh_token']
    response = requests.post('http://localhost:8000/auth/token', data=json.dumps(post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.invalid_credentials
    else:
        success = True   
        code = ResponseCodes.success 
    return JsonResponse(create_response(jsonres, success, code), safe=False)    

@csrf_exempt
@api_view(["GET"])
def sync_user_emails(request):
    profile = Profile.objects.get(user=request.user)
    if not profile.is_gmail_read_ok:
        return JsonResponse(create_response(None, False, ResponseCodes.google_token_expired), safe=False)    
    #it'll be used for background tasking in production
    #refs. https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e
    #https://django-background-tasks.readthedocs.io/en/latest/
    #https://stackoverflow.com/questions/41205607/how-to-activate-the-process-queue-in-django-background-tasks
    #scheduleFetcher.now(request.user.id)
    scheduleFetcher(request.user.id)
    return JsonResponse(create_response(None), safe=False)    

@csrf_exempt
@api_view(["GET"])
def get_linkedin_profile(request): 
    result, text = get_profile(request.user)   
    if result:
        return JsonResponse(create_response(text), safe=False) 
    else:
        return JsonResponse(create_response(None, False, ResponseCodes.user_profile_not_found))    

@background(schedule=1)
def scheduleFetcher(user_id):
    user = User.objects.get(pk=user_id)
    if user.social_auth.filter(provider='google-oauth2'):
        fetchJobApplications(user)    

@api_view(["POST"])
@csrf_exempt
def update_gmail_token(request):
    body = request.data
    token = body['token']
    try:
        user_profile = UserSocialAuth.objects.get(user=request.user)
        log(user_profile, 'i')
        if user_profile is not None:
            user_profile.extra_data['access_token'] = token
            user_profile.save()
            success = True
            profile = Profile.objects.get(user=request.user)
            profile.is_gmail_read_ok = True
            profile.save()  
            code = ResponseCodes.success
            scheduleFetcher(request.user.id)
        else:
            success = False
            code = ResponseCodes.user_profile_not_found
    except Exception as e: 
        log(e, 'e')
        success = False   
        code = ResponseCodes.couldnt_update_google_token         
    return JsonResponse(create_response(None, success, code), safe=False)    

@csrf_exempt
@api_view(["GET"])
def get_user_google_mails(request):
    mails = GoogleMail.objects.all()
    slist = GoogleMailSerializer(instance=mails, many=True).data
    return JsonResponse(create_response(slist), safe=False)    
