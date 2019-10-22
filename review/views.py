from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.utils import timezone

from company.models import Company
from company.serializers import CompanySerializer
from jobapps.models import SourceType
from jobapps.serializers import SourceSerializer
from position.models import JobPosition
from review.models import EmploymentAuth, EmploymentStatus
from utils import utils
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from utils.utils import send_notification_email_to_admins, get_boolean_from_request
from .models import Review, CompanyEmploymentAuth
from .serializers import ReviewSerializer, EmploymentAuthSerializer


@csrf_exempt
@api_view(["GET", "POST", "PUT", "PATCH"])
def reviews(request):
    body = request.data
    user = request.user
    if 'recaptcha_token' in body and utils.verify_recaptcha(user, body['recaptcha_token'],
                                                            'review') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed),
                            safe=False)
    if request.method == "GET" and user.user_type.name == 'Career Service':
        reviews_list = Review.objects.filter(is_published=False, is_rejected=False, user__college=user.college)
        return JsonResponse(create_response(data=ReviewSerializer(instance=reviews_list, many=True).data), safe=False)
    elif request.method == "PATCH":
        if request.user.user_type.name == 'Career Service':
            body = request.data
            review = Review.objects.get(pk=body['review_id'])
            approved = body['approved']
            review.is_published = approved
            review.is_rejected = not approved
            review.save()
            return JsonResponse(create_response(data=None), safe=False)
        else:
            return JsonResponse(
                create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                safe=False)
    elif request.method == "GET":
        company_id = request.GET.get('company_id')
        position_id = request.GET.get('position_id')
        all_reviews = get_boolean_from_request(request, 'all_reviews')
        review_id = request.GET.get('review_id')
        if review_id is not None:
            reviews_list = Review.objects.filter(pk=review_id, user=request.user)
            if reviews_list.count() == 0:
                return JsonResponse(
                    create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                    safe=False)
            return JsonResponse(create_response(data=ReviewSerializer(instance=reviews_list[0], many=False).data),
                                safe=False)
        elif company_id is None and position_id is None:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters),
                                safe=False)
        if company_id is None:
            reviews_list = Review.objects.filter(Q(is_published=True) | Q(
                user=request.user), position__pk=position_id)
        elif position_id is None:
            reviews_list = Review.objects.filter(Q(is_published=True) | Q(
                user=request.user), company__pk=company_id)
        else:
            if all_reviews:
                reviews_list = Review.objects.filter(
                    is_published=True, position__pk=position_id, company__pk=company_id)
            else:
                reviews_list = Review.objects.filter(
                    user=request.user, position__pk=position_id, company__pk=company_id)
                if reviews_list.count() > 0:
                    return JsonResponse(create_response(data=ReviewSerializer(instance=reviews_list[0], many=False).data),
                                        safe=False)
                else:
                    return JsonResponse(create_response(data=None), safe=False)
        return JsonResponse(create_response(data=ReviewSerializer(instance=reviews_list, many=True).data), safe=False)
    else:
        if 'company_id' not in body or 'position_id' not in body:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.invalid_parameters),
                                safe=False)

        company = Company.objects.get(pk=body['company_id'])
        position = JobPosition.objects.get(pk=body['position_id'])
        if request.method == "PUT":
            review = Review.objects.get(pk=body['review_id'])
            if review.user.pk != user.pk:
                return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.record_not_found),
                                    safe=False)
            review.update_date = timezone.now()
        elif request.method == "POST":
            review = Review()
        review.company = company
        review.position = position
        review.user = request.user
        if 'pros' in body:
            review.pros = body['pros']
        if 'cons' in body:
            review.cons = body['cons']
        if 'interview_notes' in body:
            review.interview_notes = body['interview_notes']
        if 'overall_company_experience' in body:
            review.overall_company_experience = body['overall_company_experience']
        if 'interview_difficulty' in body:
            review.interview_difficulty = body['interview_difficulty']
        if 'overall_interview_experience' in body:
            review.overall_interview_experience = body['overall_interview_experience']
        if 'anonymous' in body:
            review.anonymous = body['anonymous']
        if 'emp_auths' in body:
            for a in body['emp_auths']:
                if 'value' in a:
                    auth = EmploymentAuth.objects.get(pk=a['id'])
                    review.save()
                    if CompanyEmploymentAuth.objects.filter(review=review, employment_auth=auth).count() == 0:
                        c_auth = CompanyEmploymentAuth(
                            review=review, employment_auth=auth, value=a['value'])
                        c_auth.save()
                    else:
                        c_auth = CompanyEmploymentAuth.objects.get(
                            review=review, employment_auth=auth)
                        c_auth.value = a['value']
                        c_auth.save()
        if 'emp_status_id' in body:
            review.emp_status = EmploymentStatus.objects.get(
                pk=body['emp_status_id'])
        if 'source_type_id' in body:
            review.source_type = SourceType.objects.get(pk=body['source_type_id'])

        # publish review if there is no content to approve
        if 'pros' not in body and 'cons' not in body and 'interview_notes' not in body:
            review.is_published = True
        else:
            review.is_published = False
            send_notification_email_to_admins('review', review.user.college.id)

        review.save()
        response = {'review': ReviewSerializer(instance=review, many=False).data,
                    'company': CompanySerializer(instance=company, many=False, context={
                        'user': request.user, 'position': position}).data}
        return JsonResponse(create_response(data=response), safe=False)


@csrf_exempt
@api_view(["GET"])
def source_types(request):
    sources = SourceType.objects.all()
    return JsonResponse(create_response(data=SourceSerializer(instance=sources, many=True).data), safe=False)


@csrf_exempt
@api_view(["GET"])
def employment_authorizations(request):
    statuses = EmploymentAuth.objects.all()
    return JsonResponse(create_response(data=EmploymentAuthSerializer(instance=statuses, many=True).data), safe=False)
