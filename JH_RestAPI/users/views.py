from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
from utils.generic_json_creator import create_response
from utils.linkedin_lookup import get_linkedin_profile
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from .models import Profile
from .models import EmploymentStatus
from jobapps.models import GoogleMail
from jobapps.serializers import GoogleMailSerializer
from utils.gmail_lookup import fetchJobApplications
from background_task import background
from social_django.models import UserSocialAuth
from rest_framework.parsers import JSONParser
from utils.logger import log
from utils.error_codes import ResponseCodes
from .serializers import ProfileSerializer
from .serializers import EmploymentStatusSerializer
import traceback
from django.contrib.auth import get_user_model
from datetime import datetime


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

    if '@' in username:
        return JsonResponse(create_response(None, False, ResponseCodes.invalid_username), safe=False)  

    # Check if passwords match
    if password == password2:
        # Check username
        User = get_user_model()
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
    print(response.text)
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
    if response.status_code is 204 or response.status_code is 200:
        success = True
        code = ResponseCodes.success
    else:
        success = False   
        code = ResponseCodes.couldnt_logout_user 
    return JsonResponse(create_response(None, success, code), safe=False)

@csrf_exempt
@api_view(["POST"])
def change_password(request):    
    body = request.data
    password = body['password']
    user = request.user
    user.set_password(password)
    user.save()
    return JsonResponse(create_response(None), safe=False)

@csrf_exempt
@api_view(["POST"])
def update_profile_photo(request):    
    body = request.data
    user = request.user
    profile = Profile.objects.get(user=user)
    if 'photo_url' in body:
        profile.profile_photo = body['photo_url']
    profile.save()
    return JsonResponse(create_response(ProfileSerializer(instance=profile, many=False).data), safe=False) 

@csrf_exempt
@api_view(["POST"])
def update_profile(request):    
    body = request.data
    user = request.user
    User = get_user_model()
    profile = Profile.objects.get(user=user)
    if 'password' in body:
        user.set_password(body['password'])
    if 'username' in body:
        if User.objects.filter(username=body['username']).exists():
            return JsonResponse(create_response(None, False, ResponseCodes.username_exists), safe=False) 
        user.username = body['username']
    if 'first_name' in body:
        user.first_name = body['first_name']
    if 'last_name' in body:
        user.last_name = body['last_name']    
    if 'gender' in body:
        profile.gender = body['gender']
    if 'dob' in body:
        profile.dob = datetime.strptime(body['dob'], "%Y-%m-%d").date()    
    if 'itu_email' in body and '@students.itu.edu' in body['itu_email']:
        profile.itu_email = body['itu_email']
    if 'phone_number' in body:
        profile.phone_number = body['phone_number']
    if 'emp_status_id' in body:
        if EmploymentStatus.objects.filter(pk=body['emp_status_id']).count() > 0:
            profile.emp_status = EmploymentStatus.objects.get(pk=body['emp_status_id'])
        
    user.save()
    profile.save()
    return JsonResponse(create_response(ProfileSerializer(instance=profile, many=False).data), safe=False)    

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
def get_profile(request): 
    get_linkedin_profile(request.user)  
    profile = Profile.objects.get(user=request.user) 
    return JsonResponse(create_response(ProfileSerializer(instance=profile, many=False).data), safe=False)  

@csrf_exempt
@api_view(["GET"])
def get_employment_statuses(request): 
    statuses = EmploymentStatus.objects.all()
    return JsonResponse(create_response(EmploymentStatusSerializer(instance=statuses, many=True).data), safe=False)      

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
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        success = False   
        code = ResponseCodes.couldnt_update_google_token         
    return JsonResponse(create_response(None, success, code), safe=False)    

@csrf_exempt
@api_view(["GET"])
def get_user_google_mails(request):
    mails = GoogleMail.objects.all()
    slist = GoogleMailSerializer(instance=mails, many=True).data
    return JsonResponse(create_response(slist), safe=False)    
