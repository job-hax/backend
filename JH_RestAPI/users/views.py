from django.http import JsonResponse
import requests
import json
from utils.generic_json_creator import create_response
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import Profile
from .models import EmploymentStatus, EmploymentAuth
from .models import Feedback
from jobapps.models import GoogleMail
from jobapps.serializers import GoogleMailSerializer
from utils.gmail_lookup import fetchJobApplications
from background_task import background
from social_django.models import UserSocialAuth
from rest_framework.parsers import JSONParser
from utils.logger import log
from utils.error_codes import ResponseCodes
from .serializers import ProfileSerializer
from .serializers import EmploymentStatusSerializer, EmploymentAuthSerializer
from college.models import College
from company.models import Company
from position.models import JobPosition
from utils.models import Country, State
from college.utils import insert_or_update_major
import traceback
from django.contrib.auth import get_user_model
from datetime import datetime
from oauth2_provider.models import AccessToken
from django.contrib.auth import authenticate
from utils import utils
from django.utils import timezone
import uuid
from utils.linkedin_utils import get_access_token_with_code
from utils.clearbit_company_checker import get_company_detail


# Create your views here.
@require_POST
@csrf_exempt
def register(request):
    # Get form values
    body = JSONParser().parse(request)
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'signup') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    first_name = ''
    last_name = ''
    linkedin_auth_code = None
    google_access_token = None
    if 'first_name' in body:
        first_name = body['first_name']
    if 'last_name' in body:
        last_name = body['last_name']
    if 'linkedin_auth_code' in body:
        linkedin_auth_code = body['linkedin_auth_code']
    if 'google_access_token' in body:
        google_access_token = body['google_access_token']
    username = body['username']
    email = body['email']
    password = body['password']
    password2 = body['password2']

    if '@' in username:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_username), safe=False)

    # Check if passwords match
    if password == password2:
        # Check username
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            success = False
            code = ResponseCodes.username_exists
        else:
            if User.objects.filter(email__iexact=email).exists():
                success = False
                code = ResponseCodes.email_exists
            else:
                # Looks good
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                                last_name=last_name, approved=False, activation_key=None, key_expires=None)
                user.save()
                if linkedin_auth_code is None and google_access_token is None:
                    activation_key, expiration_time = utils.generate_activation_key_and_expiredate(
                        body['username'])
                    user.activation_key = activation_key
                    user.key_expires = expiration_time
                    user.save()
                    utils.send_email(user.email,
                                     activation_key, 'activate')

                    post_data = {'client_id': body['client_id'], 'client_secret': body['client_secret'],
                                 'grant_type': 'password',
                                 'username': username, 'password': password}

                    response = requests.post('http://localhost:8000/auth/token', data=json.dumps(
                        post_data), headers={'content-type': 'application/json'})
                    jsonres = json.loads(response.text)
                    if 'error' in jsonres:
                        success = False
                        code = ResponseCodes.couldnt_login
                    else:
                        success = True
                        code = ResponseCodes.success
                        profile = Profile.objects.get(
                            user=user)
                        jsonres['user_type'] = profile.user_type
                    return JsonResponse(create_response(data=jsonres, success=success, error_code=code), safe=False)
                else:
                    post_data = {'client_id': body['client_id'], 'client_secret': body['client_secret'],
                                 'grant_type': 'convert_token'}
                    if linkedin_auth_code is not None:
                        post_data['backend'] = 'linkedin-oauth2'
                        post_data['token'] = get_access_token_with_code(body['token'])
                    else:
                        post_data['backend'] = 'google-oauth2'
                        post_data['token'] = body['token']
                    response = requests.post('http://localhost:8000/auth/convert-token',
                                             data=json.dumps(post_data), headers={'content-type': 'application/json'})
                    jsonres = json.loads(response.text)
                    log(jsonres, 'e')
                    if 'error' in jsonres:
                        success = False
                        code = ResponseCodes.invalid_credentials
                    else:
                        success = True
                        code = ResponseCodes.success
                        user = AccessToken.objects.get(token=jsonres['access_token']).user
                        profile = Profile.objects.get(user=user)
                        jsonres['user_type'] = profile.user_type
                        user.approved = True
                        user.save()
                    return JsonResponse(create_response(data=jsonres, success=success, error_code=code), safe=False)
    else:
        success = False
        code = ResponseCodes.passwords_do_not_match
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@require_GET
@csrf_exempt
def check_credentials(request):
    User = get_user_model()
    email = request.GET.get('email')
    username = request.GET.get('username')
    error_code = ResponseCodes.invalid_parameters
    if email is not None:
        users = User.objects.filter(email=email)
        if users.count() == 0:
            return JsonResponse(create_response(data=None, success=True, error_code=ResponseCodes.success), safe=False)
        error_code = ResponseCodes.email_exists
    if username is not None:
        users = User.objects.filter(username=username)
        if users.count() == 0:
            return JsonResponse(create_response(data=None, success=True, error_code=ResponseCodes.success), safe=False)
        error_code = ResponseCodes.username_exists
    return JsonResponse(create_response(data=None, success=False, error_code=error_code), safe=False)

@require_GET
@csrf_exempt
def activate_user(request):
    try:
        User = get_user_model()
        user = User.objects.filter(activation_key=request.GET.get('code'))
        if user.count() == 0:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)
        user = user[0]
        if user.approved == False:
            if user.key_expires is None or timezone.now() > user.key_expires:
                return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)
            else:  # Activation successful
                user.approved = True
                user.activation_key = None
                user.key_expires = None
                user.save()
                return JsonResponse(create_response(data=None, success=True, error_code=ResponseCodes.success), safe=False)
        # If user is already active, simply display error message
        else:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)


@require_POST
@csrf_exempt
def generate_activation_code(request):
    body = JSONParser().parse(request)
    user = authenticate(username=body['username'], password=body['password'])
    if user is not None:
        if user.approved:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.email_already_verified), safe=False)
        else:
            activation_key, expiration_time = utils.generate_activation_key_and_expiredate(
                body['username'])
            user.activation_key = activation_key
            user.key_expires = expiration_time
            user.save()
            utils.send_email(user.email, activation_key, 'activate')
            return JsonResponse(create_response(data=None, success=True), safe=False)
    else:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_credentials), safe=False)


@require_POST
@csrf_exempt
def forgot_password(request):
    body = JSONParser().parse(request)
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'forgot_password') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    username = body['username']
    User = get_user_model()
    try:
        user = User.objects.get(
            Q(username__iexact=username) | Q(email__iexact=username))
        activation_key, expiration_time = utils.generate_activation_key_and_expiredate(
            user.username)
        user.forgot_password_key = activation_key
        user.forgot_password_key_expires = expiration_time
        user.save()
        utils.send_email(user.email, activation_key,
                         'check_forgot_password')
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
    return JsonResponse(create_response(data=None, success=True), safe=False)


@require_GET
@csrf_exempt
def check_forgot_password(request):
    try:
        User = get_user_model()
        user = User.objects.filter(forgot_password_key=request.GET.get('code'))
        if user.count() == 0:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)
        user = user[0]
        if user.forgot_password_key_expires is None or timezone.now() > user.forgot_password_key_expires:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)
        else:
            return JsonResponse(create_response(data=None, success=True, error_code=ResponseCodes.success), safe=False)
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)


@require_POST
@csrf_exempt
def reset_password(request):
    body = JSONParser().parse(request)
    password = body['password']
    code = body['code']
    User = get_user_model()
    user = User.objects.filter(forgot_password_key=code)
    if user.count() == 0:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_credentials), safe=False)
    user = user[0]
    user.forgot_password_key = None
    user.forgot_password_key_expires = None
    user.set_password(password)
    user.save()
    return JsonResponse(create_response(data=None), safe=False)


@require_POST
@csrf_exempt
def login(request):
    body = JSONParser().parse(request)

    post_data = {'client_id': body['client_id'], 'client_secret': body['client_secret'], 'grant_type': 'password',
                 'username': body['username'], 'password': body['password']}
    user = authenticate(username=body['username'], password=body['password'])
    if user is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_credentials), safe=False)
    #if not user.approved:
    #    return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.email_verification_required), safe=False)
    if 'recaptcha_token' in body and utils.verify_recaptcha(user.email, body['recaptcha_token'], 'signin') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    response = requests.post('http://localhost:8000/auth/token', data=json.dumps(
        post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.couldnt_login
    else:
        success = True
        code = ResponseCodes.success
        profile = Profile.objects.get(
            user=user)
        jsonres['user_type'] = profile.user_type
        profile.save()
    return JsonResponse(create_response(data=jsonres, success=success, error_code=code), safe=False)


@require_POST
@csrf_exempt
def logout(request):
    body = JSONParser().parse(request)
    post_data = {'token': body['token'], 'client_id': body['client_id'],
                 'client_secret': body['client_secret']}
    headers = {'content-type': 'application/json'}
    response = requests.post('http://localhost:8000/auth/revoke-token',
                             data=json.dumps(post_data), headers=headers)
    if response.status_code is 204 or response.status_code is 200:
        success = True
        code = ResponseCodes.success
    else:
        success = False
        code = ResponseCodes.couldnt_logout_user
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def change_password(request):
    body = request.data
    password = body['password']
    user = request.user
    user.set_password(password)
    user.save()
    return JsonResponse(create_response(data=None), safe=False)


@csrf_exempt
@api_view(["POST"])
def update_profile_photo(request):
    body = request.data
    user = request.user
    profile = Profile.objects.get(user=user)
    if 'photo_url' in body:
        profile.profile_photo_social = body['photo_url']
    if 'photo' in body:
        f = request.data['photo']
        ext = f.name.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        profile.profile_photo_custom.save(filename, f, save=True)
    profile.save()
    return JsonResponse(create_response(data=ProfileSerializer(instance=profile, many=False).data), safe=False)


@csrf_exempt
@api_view(["POST"])
def update_profile(request):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(request.user.email, body['recaptcha_token'], 'update_profile') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    user = request.user
    User = get_user_model()
    profile = Profile.objects.get(user=user)
    if 'password' in body:
        user.set_password(body['password'])
    if 'username' in body:
        if User.objects.filter(username=body['username']).exists():
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.username_exists), safe=False)
        user.username = body['username']
    if 'first_name' in body:
        user.first_name = body['first_name']
    if 'last_name' in body:
        user.last_name = body['last_name']
    if 'gender' in body:
        profile.gender = body['gender']
    if 'dob' in body:
        profile.dob = datetime.strptime(body['dob'], "%Y-%m-%d").date()
    if 'student_email' in body:
        profile.student_email = body['student_email']
    if 'phone_number' in body:
        profile.phone_number = body['phone_number']
    if 'emp_status_id' in body:
        if EmploymentStatus.objects.filter(pk=body['emp_status_id']).count() > 0:
            profile.emp_status = EmploymentStatus.objects.get(
                pk=body['emp_status_id'])

    user.save()
    profile.save()
    return JsonResponse(create_response(data=ProfileSerializer(instance=profile, many=False).data), safe=False)


@csrf_exempt
@api_view(["POST"])
def update_user_profile_and_type(request):
    body = request.data
    user = request.user
    profile = Profile.objects.get(user=user)
    profile.user_type = body['user_type']
    if 'college_id' in body:
        if College.objects.filter(pk=body['college_id']).count() > 0:
            profile.college = College.objects.get(
                pk=body['college_id'])
    if 'major' in body:
        profile.major = insert_or_update_major(body['major'])
    if 'grad_year' in body:
        profile.grad_year = body['grad_year']
    if 'job_title' in body:
        job_title = body['job_title']
        # jt is current dummy job title in the db
        jt = JobPosition.objects.all().filter(job_title__iexact=job_title)
        if jt is None or len(jt) == 0:
            jt = JobPosition(job_title=job_title)
            jt.save()
        else:
            jt = jt[0]
        profile.job_position = jt
    if 'company' in body:
        company = body['company']
        # check if the company details already exists in the db
        cd = get_company_detail(company)
        if cd is None:
            company_title = company
        else:
            company_title = cd['name']
        jc = Company.objects.all().filter(cb_name__iexact=company_title)
        if jc is None or len(jc) == 0:
            # if company doesnt exist save it
            if cd is None:
                jc = Company(company=company, company_logo=None,
                             cb_name=company, cb_company_logo=None, cb_domain=None)
            else:
                jc = Company(company=company, company_logo=None,
                             cb_name=cd['name'], cb_company_logo=cd['logo'], cb_domain=cd['domain'])
            jc.save()
        else:
            jc = jc[0]
        profile.company = jc

    if 'country_id' in body and 'state_id' in body:
        state = State.objects.get(pk=body['state_id'])
        if state.country.id != body['country_id']:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters),
                                safe=False)
        country = Country.objects.get(pk=body['country_id'])
        profile.country = country
        profile.state = state

    profile.save()
    return JsonResponse(create_response(data=ProfileSerializer(instance=profile, many=False).data), safe=False)


@csrf_exempt
@api_view(["POST"])
def link_social_account(request):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'signin') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    post_data = {'client_id': body['client_id'], 'client_secret': body['client_secret'], 'grant_type': 'convert_token'}
    provider = body['provider']
    post_data['backend'] = provider
    if provider == 'linkedin-oauth2':
        if request.user.social_auth.filter(provider='linkedin-oauth2').count() == 0:
            post_data['token'] = get_access_token_with_code(body['token'])
        else:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.account_already_linked), safe=False)
    else:
        if request.user.social_auth.filter(provider='google-oauth2').count() == 0:
            post_data['token'] = body['token']
        else:
            return JsonResponse(
                create_response(data=None, success=False, error_code=ResponseCodes.account_already_linked), safe=False)
    response = requests.post('http://localhost:8000/auth/convert-token',
                             data=json.dumps(post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    log(jsonres, 'e')
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.invalid_credentials
    else:
        success = True
        code = ResponseCodes.success
        social_user = UserSocialAuth.objects.get(extra_data__icontains=post_data['token'])

        if social_user.user.email != request.user.email:
            social_user.user.delete()

        social_user.user = request.user
        social_user.save()



        post_data = {'token': jsonres['access_token'], 'client_id': body['client_id'],
                     'client_secret': body['client_secret']}
        headers = {'content-type': 'application/json'}
        response = requests.post('http://localhost:8000/auth/revoke-token',
                                 data=json.dumps(post_data), headers=headers)

        log(str(response), 'e')
        if provider == 'google-oauth2':
            profile = Profile.objects.get(user=request.user)
            profile.is_gmail_read_ok = True
            profile.synching = True
            profile.save()
            scheduleFetcher(request.user.id)
        profile = Profile.objects.get(user=request.user)
        return JsonResponse(create_response(data=ProfileSerializer(instance=profile, many=False).data), safe=False)
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@require_POST
@csrf_exempt
def auth_social_user(request):
    body = JSONParser().parse(request)
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'signin') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    post_data = {'client_id': body['client_id'], 'client_secret': body['client_secret'], 'grant_type': 'convert_token'}
    provider = body['provider']
    post_data['backend'] = provider
    if provider == 'linkedin-oauth2':
        post_data['token'] = get_access_token_with_code(body['token'])
    else:
        post_data['token'] = body['token']
    response = requests.post('http://localhost:8000/auth/convert-token',
                             data=json.dumps(post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    log(jsonres, 'e')
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.invalid_credentials
    else:
        success = True
        code = ResponseCodes.success
        user = AccessToken.objects.get(token=jsonres['access_token']).user
        profile = Profile.objects.get(user=user)
        jsonres['user_type'] = profile.user_type
        profile.save()
        user.approved = True
        user.save()
        if provider == 'google-oauth2':
            profile.is_gmail_read_ok = True
            profile.synching = True
            profile.save()
            scheduleFetcher(user.id)
    return JsonResponse(create_response(data=jsonres, success=success, error_code=code), safe=False)


@background(schedule=1)
def scheduleFetcher(user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    if user.social_auth.filter(provider='google-oauth2'):
        fetchJobApplications(user)


@csrf_exempt
@api_view(["GET"])
def sync_user_emails(request):
    profile = Profile.objects.get(user=request.user)
    if not profile.is_gmail_read_ok:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.google_token_expired), safe=False)
    # it'll be used for background tasking in production
    # refs. https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e
    # https://django-background-tasks.readthedocs.io/en/latest/
    # https://stackoverflow.com/questions/41205607/how-to-activate-the-process-queue-in-django-background-tasks
    # scheduleFetcher.now(request.user.id)
    profile.synching = True
    profile.save()
    scheduleFetcher(request.user.id)
    return JsonResponse(create_response(data=None), safe=False)


@require_POST
@csrf_exempt
def refresh_token(request):
    body = JSONParser().parse(request)
    post_data = {'client_id': body['client_id']}
    post_data['client_secret'] = body['client_secret']
    post_data['grant_type'] = 'refresh_token'
    post_data['refresh_token'] = body['refresh_token']
    response = requests.post('http://localhost:8000/auth/token', data=json.dumps(
        post_data), headers={'content-type': 'application/json'})
    jsonres = json.loads(response.text)
    if 'error' in jsonres:
        success = False
        code = ResponseCodes.invalid_credentials
    else:
        success = True
        code = ResponseCodes.success
    return JsonResponse(create_response(data=jsonres, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_profile(request):
    profile = Profile.objects.get(user=request.user)
    return JsonResponse(create_response(data=ProfileSerializer(instance=profile, many=False).data), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_employment_statuses(request):
    statuses = EmploymentStatus.objects.all()
    return JsonResponse(create_response(data=EmploymentStatusSerializer(instance=statuses, many=True).data), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_employment_auths(request):
    statuses = EmploymentAuth.objects.all()
    return JsonResponse(create_response(data=EmploymentAuthSerializer(instance=statuses, many=True).data), safe=False)


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
            profile = Profile.objects.get(user=request.user)
            profile.synching = True
            profile.save()
            scheduleFetcher(request.user.id)
        else:
            success = False
            code = ResponseCodes.user_profile_not_found
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        success = False
        code = ResponseCodes.couldnt_update_google_token
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_user_google_mails(request):
    mails = GoogleMail.objects.all()
    slist = GoogleMailSerializer(instance=mails, many=True).data
    return JsonResponse(create_response(data=slist), safe=False)


@csrf_exempt
@api_view(["POST"])
def feedback(request):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(request.user.email, body['recaptcha_token'], 'feedback') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    text = body['text']
    star = body['star']
    user = request.user
    Feedback.objects.create(user=user, text=text, star=star)
    return JsonResponse(create_response(data=None), safe=False)


@csrf_exempt
@api_view(["POST"])
def verify_recaptcha(request):
    body = request.data
    if 'recaptcha_token' not in body or 'action' not in body:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)
    elif utils.verify_recaptcha(request.user.email, body['recaptcha_token'], body['action']) == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)
    else:
        return JsonResponse(create_response(data=None, success=True), safe=False)
