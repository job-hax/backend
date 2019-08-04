from django.http import JsonResponse
from utils.generic_json_creator import create_response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import JobApplication, Contact, ApplicationStatus, StatusHistory
from .models import Source
from .models import JobApplicationNote
from users.models import Profile
from position.models import JobPosition
from company.models import Company
from utils.clearbit_company_checker import get_company_detail
from .serializers import JobApplicationSerializer, ContactSerializer
from .serializers import ApplicationStatusSerializer
from .serializers import StatusHistorySerializer
from .serializers import JobApplicationNoteSerializer
from .serializers import SourceSerializer
from utils.logger import log
from datetime import datetime
from utils.error_codes import ResponseCodes
import traceback
from utils import utils


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
def get_new_jobapps(request):
    timestamp = request.GET.get('timestamp')
    timestamp = int(timestamp) / 1000
    if timestamp is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters))
    profile = Profile.objects.get(user=request.user)
    time = datetime.fromtimestamp(int(timestamp))
    user_job_apps = JobApplication.objects.filter(created__gte=time)
    joblist = JobApplicationSerializer(instance=user_job_apps, many=True, context={
                                       'user': request.user}).data
    response = {'data': joblist, 'synching': profile.synching}
    return JsonResponse(create_response(data=response), safe=False)


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
def get_contacts(request):
    jobapp_id = request.GET.get('jobapp_id')
    success = True
    code = ResponseCodes.success
    slist = []
    if jobapp_id is None:
        success = False
        code = ResponseCodes.invalid_parameters
    else:
        contacts = Contact.objects.filter(job_post__pk=jobapp_id)
        try:
            slist = ContactSerializer(instance=contacts, many=True).data
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
    jobapp_ids = []
    if 'jobapp_ids' in body:
        jobapp_ids = body['jobapp_ids']
    if 'jobapp_id' in body:
        jobapp_ids.append(body['jobapp_id'])
    success = True
    code = ResponseCodes.success
    if len(jobapp_ids) == 0:
        success = False
        code = ResponseCodes.record_not_found
    elif rejected is None and status_id is None:
        success = False
        code = ResponseCodes.record_not_found
    else:
        user_job_apps = JobApplication.objects.filter(pk__in=jobapp_ids)
        if user_job_apps.count() == 0:
            success = False
            code = ResponseCodes.record_not_found
        else:
            for user_job_app in user_job_apps:
                if user_job_app.user == request.user:
                    if status_id is None:
                        user_job_app.isRejected = rejected
                    else:
                        new_status = ApplicationStatus.objects.filter(pk=status_id)
                        if new_status.count() == 0:
                            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters),
                                                safe=False)
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
                #else:
                #    success = False
                #    code = ResponseCodes.record_not_found
    return JsonResponse(create_response(data=None, success=success, error_code=code), safe=False)


@csrf_exempt
@api_view(["POST"])
def delete_jobapp(request):
    body = request.data
    jobapp_ids = []
    if 'jobapp_ids' in body:
        jobapp_ids = body['jobapp_ids']
    if 'jobapp_id' in body:
        jobapp_ids.append(body['jobapp_id'])
    success = True
    code = ResponseCodes.success
    if len(jobapp_ids) == 0:
        success = False
        code = ResponseCodes.record_not_found
    else:
        user_job_apps = JobApplication.objects.filter(pk__in=jobapp_ids)
        if user_job_apps.count() == 0:
            success = False
            code = ResponseCodes.record_not_found
        else:
            for user_job_app in user_job_apps:
                if user_job_app.user == request.user:
                    user_job_app.deleted_date = datetime.now()
                    user_job_app.isDeleted = True
                    user_job_app.save()
                #else:
                #    success = False
                #    code = ResponseCodes.record_not_found
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


@csrf_exempt
@api_view(["POST"])
def update_contact(request):
    body = request.data
    contact_id = body.get('contact_id')
    if contact_id is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters),
                            safe=False)
    try:
        contact = Contact.objects.get(pk=contact_id)
        if contact.job_post.user == request.user:
            name = body.get('name')
            if name is not None:
                contact.name = name
            phone_number = body.get('phone_number')
            if phone_number is not None:
                contact.phone_number = phone_number
            linkedin_url = body.get('linkedin_url')
            if linkedin_url is not None:
                contact.linkedin_url = linkedin_url
            description = body.get('description')
            if description is not None:
                contact.description = description
            job_title = body.get('job_title')
            if job_title is not None:
                # jt is current dummy job title in the db
                jt = JobPosition.objects.all().filter(job_title__iexact=job_title)
                if jt is None or len(jt) == 0:
                    jt = JobPosition(job_title=job_title)
                    jt.save()
                else:
                    jt = jt[0]
                contact.position = jt
            company = body.get('company')
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
                contact.company = jc

            contact.update_date = datetime.now()
            contact.save()
            data = ContactSerializer(
                instance=contact, many=False).data
            return JsonResponse(create_response(data=data, success=True, error_code=ResponseCodes.success), safe=False)
        else:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                                safe=False)
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)


@csrf_exempt
@api_view(["POST"])
def delete_contact(request):
    body = request.data
    contact_id = body.get('contact_id')
    if contact_id is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters),
                            safe=False)
    user_job_app_contact = Contact.objects.filter(
        pk=contact_id)
    if user_job_app_contact.count() == 0:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)
    user_job_app_contact = user_job_app_contact[0]
    if user_job_app_contact.job_post.user == request.user:
        user_job_app_contact.delete()
        return JsonResponse(create_response(data=None, success=True, error_code=ResponseCodes.success), safe=False)
    else:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)


@csrf_exempt
@api_view(["POST"])
def add_contact(request):
    body = request.data

    jobapp_id = body.get('jobapp_id')
    name = body.get('name')
    if jobapp_id is None or name is None:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters), safe=False)
    try:
        user_job_app = JobApplication.objects.get(pk=jobapp_id)
        if user_job_app.user == request.user:
            phone_number = body.get('phone_number')
            linkedin_url = body.get('linkedin_url')
            description = body.get('description')
            job_title = body.get('job_title')
            jt = None
            jc = None
            if job_title is not None:
                # jt is current dummy job title in the db
                jt = JobPosition.objects.all().filter(job_title__iexact=job_title)
                if jt is None or len(jt) == 0:
                    jt = JobPosition(job_title=job_title)
                    jt.save()
                else:
                    jt = jt[0]
            company = body.get('company')
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

            contact = Contact(
                job_post=user_job_app, name=name, phone_number=phone_number, linkedin_url=linkedin_url,description=description,
                position=jt, company=jc)
            contact.save()
            data = ContactSerializer(
                instance=contact, many=False).data
            return JsonResponse(create_response(data=data), safe=False)
        else:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found), safe=False)
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                            safe=False)
