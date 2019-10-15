from background_task import background
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from utils.logger import log
import random
from college.serializers import CollegeSerializer
from college.models import College
from blog.models import Blog
from event.models import Event
from jobapps.models import JobApplication
from poll.models import Vote
from review.models import Review
from utils.generic_json_creator import create_response
from users.serializers import UserTypeSerializer
from users.models import UserType
from .serializers import *
import requests
from utils.error_codes import ResponseCodes
from rest_framework.parsers import JSONParser

User = get_user_model()


@require_GET
def agreements(request):
    agreements = Agreement.objects.all()
    slist = AgreementSerializer(instance=agreements, many=True).data
    response = {}
    for s in slist:
        response[s['key']] = s
    return JsonResponse(create_response(data=response), safe=False)


def duplicate_user(demo_user, username, new_username):
    email = new_username + '@jobhax.com'
    demo_user.username = new_username
    demo_user.email = email
    demo_user.pk = None
    demo_user.set_password('123456')
    demo_user.save()

    user = User.objects.get(username=new_username)
    demo_user = User.objects.get(username=username)

    blogs = Blog.objects.filter(publisher_profile=demo_user)
    for blog in blogs:
        blog.pk = None
        blog.publisher_profile = user
        blog.save()
    events = Event.objects.filter(host_user=demo_user)
    for event in events:
        event.pk = None
        event.host_user = user
        event.save()
    job_apps = JobApplication.objects.filter(user=demo_user)
    for job_app in job_apps:
        job_app.pk = None
        job_app.user = user
        job_app.save()
    reviews = Review.objects.filter(user=demo_user)
    for review in reviews:
        review.pk = None
        review.user = user
        review.save()


@require_POST
@csrf_exempt
def demo(request):
    body = JSONParser().parse(request)

    demo_count = User.objects.filter(username__startswith='demo').count()
    if demo_count > 51:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user), safe=False)

    if 'user_type_id' in body:
        main_account_username = 'demo_' + UserType.objects.get(pk=body['user_type_id']).name.lower()
        if User.objects.filter(username=main_account_username).count() == 0:
            demo_user = User.objects.get(username='demo')
            duplicate_user(demo_user, 'demo', main_account_username)
            user = User.objects.get(username=main_account_username)
            user.user_type = UserType.objects.get(pk=body['user_type_id'])
            user.save()
    else:
        main_account_username = 'demo'

    demo_user = User.objects.get(username=main_account_username)

    username = main_account_username + str(random.randint(10000,99999))
    if User.objects.filter(username=username).count() > 0:
        username = main_account_username + str(random.randint(10000, 99999))

    duplicate_user(demo_user, main_account_username, username)

    post_data = {'client_id': body['client_id'], 'client_secret': body['client_secret'],
                 'grant_type': 'password',
                 'username': username, 'password': '123456'}

    response = requests.post('http://localhost:8000/auth/token', data=json.dumps(
        post_data), headers={'content-type': 'application/json'})
    json_res = json.loads(response.text)
    if 'error' in json_res:
        success = False
        code = ResponseCodes.couldnt_login
    else:
        success = True
        code = ResponseCodes.success
        user = User.objects.get(username=username)
        json_res['user_type'] = UserTypeSerializer(instance=user.user_type, many=False).data
        json_res['signup_flow_completed'] = user.signup_flow_completed
        schedule_delete_demo_account(user.id)
    return JsonResponse(create_response(data=json_res, success=success, error_code=code), safe=False)


@background(schedule=3600)
def schedule_delete_demo_account(user_id):
    user = User.objects.get(pk=user_id)
    Blog.objects.filter(publisher_profile=user).delete()
    Event.objects.filter(host_user=user).delete()
    JobApplication.objects.filter(user=user).delete()
    Vote.objects.filter(user=user).delete()
    Review.objects.filter(user=user).delete()
    user.delete()


@require_GET
@csrf_exempt
def countries(request):
    countries = Country.objects.all()
    slist = CountrySerializer(instance=countries, many=True).data
    return JsonResponse(create_response(data=slist), safe=False)


@require_GET
@csrf_exempt
def states(request, country_pk):
    states = State.objects.filter(country__pk=country_pk)
    slist = StateSerializer(instance=states, many=True).data
    return JsonResponse(create_response(data=slist), safe=False)


@require_GET
@csrf_exempt
def feedbacks(request):
    feedback_question = FeedbackQuestion.objects.first()
    if feedback_question is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found), safe=False)
    feedback_question = FeedbackQuestionSerializer(instance=feedback_question, many=False).data
    return JsonResponse(create_response(data=feedback_question), safe=False)


@require_POST
@csrf_exempt
def answer_feedback(request, feedback_pk):
    feedback_question = FeedbackQuestion.objects.filter(pk=feedback_pk)
    if feedback_question.count() == 0:
        return JsonResponse(
            create_response(data=None, success=False, error_code=ResponseCodes.record_not_found), safe=False)
    feedback_question = feedback_question[0]
    body = JSONParser().parse(request)
    if 'item_id' not in body:
        return JsonResponse(
            create_response(data=None, success=False, error_code=ResponseCodes.missing_item_id_parameter), safe=False)
    item_pk = body['item_id']
    item = FeedbackQuestionItem.objects.get(pk=item_pk)

    user_input = ''
    if 'user_input' in body:
        user_input = body['user_input']

    FeedbackAnswer.objects.create(
        feedback_question=feedback_question,
        ip=request.META['REMOTE_ADDR'],
        user_input=user_input,
        answer=item,
    )

    return JsonResponse(create_response(data=None), safe=False)


@require_GET
@csrf_exempt
def customizations(request):
    host = request.get_host()
    log(host, 'e')
    if host.startswith('localhost'):
        return JsonResponse(create_response(data=CollegeSerializer(instance=College.objects.get(name='JobHax'), many=False).data), safe=False)
    else:
        return JsonResponse(
            create_response(data=CollegeSerializer(instance=College.objects.get(jobhax_domain=host), many=False).data),
            safe=False)