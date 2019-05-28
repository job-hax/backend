from django.http import JsonResponse
from utils.generic_json_creator import create_response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import JobApplication
from .models import ApplicationStatus
from .models import StatusHistory
from .models import Source
from .models import JobApplicationNote
from position.models import JobPosition
from company.models import Company
from utils.clearbit_company_checker import get_company_detail
from .serializers import JobApplicationSerializer
from .serializers import ApplicationStatusSerializer
from .serializers import StatusHistorySerializer
from .serializers import JobApplicationNoteSerializer
from .serializers import SourceSerializer
from utils.logger import log
from datetime import datetime
from utils.error_codes import ResponseCodes
import traceback
from utils import utils


# Create your views here.
@csrf_exempt
@api_view(["GET"])
def get_jobapps(request):
    status_id = request.GET.get('status_id')
    if status_id is not None:
        user_job_apps = JobApplication.objects.filter(
            applicationStatus_id=status_id, user_id=request.user.id, isDeleted=False).order_by('-applyDate')
    else:
        user_job_apps = JobApplication.objects.filter(
            user_id=request.user.id, isDeleted=False).order_by('-applyDate')
    joblist = JobApplicationSerializer(instance=user_job_apps, many=True, context={
                                       'user': request.user}).data
    return JsonResponse(create_response(data=joblist), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_statuses(request):
    statuses = ApplicationStatus.objects.all()
    slist = ApplicationStatusSerializer(instance=statuses, many=True).data
    return JsonResponse(create_response(data=slist), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_sources(request):
    sources = Source.objects.all()
    slist = SourceSerializer(instance=sources, many=True).data
    return JsonResponse(create_response(data=slist), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_status_history(request):
    jobapp_id = request.GET.get('jopapp_id')
    success = True
    code = ResponseCodes.success
    slist = []
    if jobapp_id is None:
        success = False
        code = ResponseCodes.invalid_parameters
    else:
        statuses = StatusHistory.objects.filter(job_post__pk=jobapp_id)
        try:
            slist = StatusHistorySerializer(instance=statuses, many=True).data
        except Exception as e:
            log(traceback.format_exception(None, e, e.__traceback__), 'e')
            success = False
            code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=slist, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["GET"])
def get_jobapp_notes(request):
    jobapp_id = request.GET.get('jopapp_id')
    success = True
    code = ResponseCodes.success
    slist = []
    if jobapp_id is None:
        success = False
        code = ResponseCodes.invalid_parameters
    else:
        notes = JobApplicationNote.objects.filter(
            job_post__pk=jobapp_id).order_by('-update_date', '-created_date')
        try:
            slist = JobApplicationNoteSerializer(
                instance=notes, many=True).data
        except Exception as e:
            log(traceback.format_exception(None, e, e.__traceback__), 'e')
            success = False
            code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=slist, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def update_jobapp_note(request):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'jobapp_note') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    jobapp_note_id = body['jobapp_note_id']
    description = body['description']
    success = True
    code = ResponseCodes.success
    data = None
    if jobapp_note_id is None:
        success = False
        code = ResponseCodes.invalid_parameters
    else:
        try:
            note = JobApplicationNote.objects.get(pk=jobapp_note_id)
            if note.job_post.user == request.user:
                note.description = description
                note.update_date = datetime.now()
                note.save()
                data = JobApplicationNoteSerializer(
                    instance=note, many=False).data
            else:
                success = False
                code = ResponseCodes.record_not_found
        except Exception as e:
            log(traceback.format_exception(None, e, e.__traceback__), 'e')
            success = False
            code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=data, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def delete_jobapp_note(request):
    body = request.data
    jobapp_note_id = body['jobapp_note_id']
    success = True
    code = ResponseCodes.success
    if jobapp_note_id is None:
        success = False
        code = ResponseCodes.invalid_parameters
    else:
        user_job_app_note = JobApplicationNote.objects.filter(
            pk=jobapp_note_id)
        if len(user_job_app_note) == 0:
            success = False
            code = ResponseCodes.record_not_found
        else:
            user_job_app_note = user_job_app_note[0]
            if user_job_app_note.job_post.user == request.user:
                user_job_app_note.delete()
            else:
                success = False
                code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def add_jobapp_note(request):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'jobapp_note') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    jobapp_id = body['jobapp_id']
    description = body['description']
    success = True
    code = ResponseCodes.success
    data = None
    if jobapp_id is None or description is None:
        success = False
        code = ResponseCodes.invalid_parameters
    else:
        try:
            user_job_app = JobApplication.objects.get(pk=jobapp_id)
            if user_job_app.user == request.user:
                note = JobApplicationNote(
                    job_post=user_job_app, description=description)
                note.save()
                data = JobApplicationNoteSerializer(
                    instance=note, many=False).data
            else:
                success = False
                code = ResponseCodes.record_not_found
        except Exception as e:
            log(traceback.format_exception(None, e, e.__traceback__), 'e')
            success = False
            code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=data, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def update_jobapp(request):
    body = request.data
    status_id = body.get('status_id')
    rejected = body.get('rejected')
    jobapp_id = body.get('jobapp_id')
    success = True
    code = ResponseCodes.success
    if jobapp_id is None:
        success = False
        code = ResponseCodes.record_not_found
    elif rejected is None and status_id is None:
        success = False
        code = ResponseCodes.record_not_found
    else:
        user_job_app = JobApplication.objects.filter(pk=jobapp_id)
        if len(user_job_app) == 0:
            success = False
            code = ResponseCodes.record_not_found
        else:
            user_job_app = user_job_app[0]
            if user_job_app.user == request.user:
                if status_id is None:
                    user_job_app.isRejected = rejected
                else:
                    new_status = ApplicationStatus.objects.filter(pk=status_id)
                    if len(new_status) == 0:
                        success = False
                        code = ResponseCodes.record_not_found
                    else:
                        if rejected is None:
                            user_job_app.applicationStatus = new_status[0]
                        else:
                            user_job_app.applicationStatus = new_status[0]
                            user_job_app.isRejected = rejected
                        status_history = StatusHistory(
                            job_post=user_job_app, applicationStatus=new_status[0])
                        status_history.save()
                if rejected is not None:
                    user_job_app.rejected_date = datetime.now()
                user_job_app.updated_date = datetime.now()
                user_job_app.save()
            else:
                success = False
                code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def delete_jobapp(request):
    body = request.data
    jobapp_id = body['jobapp_id']
    success = True
    code = ResponseCodes.success
    if jobapp_id is None:
        success = False
        code = ResponseCodes.record_not_found
    else:
        user_job_app = JobApplication.objects.filter(pk=jobapp_id)
        if len(user_job_app) == 0:
            success = False
            code = ResponseCodes.record_not_found
        else:
            user_job_app = user_job_app[0]
            if user_job_app.user == request.user:
                user_job_app.deleted_date = datetime.now()
                user_job_app.isDeleted = True
                user_job_app.save()
            else:
                success = False
                code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def add_jobapp(request):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'], 'add_job') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed), safe=False)

    job_title = body['job_title']
    company = body['company']
    applicationdate = body['application_date']
    status = int(body['status_id'])
    source = body['source']
    # jt is current dummy job title in the db
    jt = JobPosition.objects.all().filter(job_title__iexact=job_title)
    if jt is None or len(jt) == 0:
        jt = JobPosition(job_title=job_title)
        jt.save()
    else:
        jt = jt[0]
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

    if Source.objects.filter(value__iexact=source).count() == 0:
        source = Source.objects.create(value=source)
    else:
        source = Source.objects.get(value__iexact=source)

    japp = JobApplication(position=jt, companyObject=jc, applyDate=applicationdate,
                          msgId='', app_source=source, user=request.user)
    japp.applicationStatus = ApplicationStatus.objects.get(pk=status)
    japp.save()
    return JsonResponse(create_response(data=JobApplicationSerializer(instance=japp, many=False, context={'user': request.user}).data), safe=False)


@csrf_exempt
@api_view(["POST"])
def edit_jobapp(request):
    body = request.data
    jobapp_id = body.get('jobapp_id')
    if jobapp_id is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found), safe=False)
    user_job_app = JobApplication.objects.filter(pk=jobapp_id)
    if user_job_app.count() == 0:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)
    user_job_app = user_job_app[0]

    if user_job_app.user != request.user:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)
    if user_job_app.msgId is not None and user_job_app.msgId != '':
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)

    job_title = body.get('job_title')
    company = body.get('company')
    applicationdate = body.get('application_date')
    source = body.get('source')

    if applicationdate is not None:
        user_job_app.applyDate =applicationdate

    if job_title is not None:
        # jt is current dummy job title in the db
        jt = JobPosition.objects.all().filter(job_title__iexact=job_title)
        if jt is None or len(jt) == 0:
            jt = JobPosition(job_title=job_title)
            jt.save()
        else:
            jt = jt[0]
        user_job_app.position = jt

    if company is not None:
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
        user_job_app.companyObject = jc

    if source is not None:
        if Source.objects.filter(value__iexact=source).count() == 0:
            source = Source.objects.create(value=source)
        else:
            source = Source.objects.get(value__iexact=source)
        user_job_app.app_source = source
    user_job_app.updated_date = datetime.now()
    user_job_app.save()
    return JsonResponse(create_response(data=JobApplicationSerializer(instance=user_job_app, many=False, context={'user': request.user}).data), safe=False)
