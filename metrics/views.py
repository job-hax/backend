import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from company.serializers import CompanyBasicsSerializer
from company.models import Company
from jobapps.models import ApplicationStatus
from jobapps.models import JobApplication
from jobapps.models import Source
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request


@csrf_exempt
@api_view(["GET"])
def company_locations(request):
    if request.user.user_type.name == 'Career Service':
        User = get_user_model()
        college_users = User.objects.filter(
            id__in=[p.id for p in User.objects.filter(college=request.user.college, is_demo=False)])
        jobapps = JobApplication.objects.filter(~Q(company_object__location_address=None),
                                                user__in=college_users, is_deleted=False).distinct('company_object')
    else:
        jobapps = JobApplication.objects.filter(~Q(company_object__location_address=None), user=request.user,
                                                is_deleted=False).distinct('company_object')
    companies = []
    for jobapp in jobapps:
        companies.append(jobapp.company_object)
    return JsonResponse(
        create_response(
            data=CompanyBasicsSerializer(instance=companies, many=True, context={'user': request.user}).data),
        safe=False)


@csrf_exempt
@api_view(["GET"])
def generic(request):
    response = []
    total_jobs_applied = JobApplication.objects.filter(user=request.user, is_deleted=False)
    for graph in range(4):
        item = {}
        if graph == 0:
            item['graph'] = {}
            item['graph']['type'] = 'pie'
            item['graph']['legend'] = []
            item['graph']['series'] = []
            item['title'] = 'Phone Screen Rate'
            if total_jobs_applied.count() == 0:
                item['value'] = '0%'
            else:
                item['value'] = str(round(total_jobs_applied.filter(
                    application_status__value='PHONE SCREEN').count() / total_jobs_applied.count() * 100, 2)) + '%'
            item['description'] = '13% INCREASE from last month'
            statuses = total_jobs_applied.filter(~Q(application_status=None)).values(
                'application_status').annotate(count=Count('pk'))
            for status in statuses:
                status_text = ApplicationStatus.objects.get(
                    pk=status['application_status']).value.upper()
                item['graph']['legend'].append(status_text)
                serie = {'name': status_text, 'value': status['count']}
                if status_text == 'PHONE SCREEN':
                    serie['selected'] = True
                item['graph']['series'].append(serie)
        elif graph == 1:
            item['graph'] = {}
            item['graph']['type'] = 'pie'
            item['graph']['legend'] = []
            item['graph']['series'] = []
            item['title'] = 'Onsite Interview Rate'
            if total_jobs_applied.count() == 0:
                item['value'] = '0%'
            else:
                item['value'] = str(round(total_jobs_applied.filter(
                    application_status__value='ONSITE INTERVIEW').count() / total_jobs_applied.count() * 100, 2)) + '%'
            item['description'] = '4% DECREASE from last month'
            statuses = total_jobs_applied.filter(~Q(application_status=None)).values(
                'application_status').annotate(count=Count('pk'))
            for status in statuses:
                status_text = ApplicationStatus.objects.get(
                    pk=status['application_status']).value.upper()
                item['graph']['legend'].append(status_text)
                serie = {'name': status_text, 'value': status['count']}
                if status_text == 'ONSITE INTERVIEW':
                    serie['selected'] = True
                item['graph']['series'].append(serie)
        elif graph == 2:
            item['graph'] = {}
            item['graph']['type'] = 'line'
            item['graph']['series'] = []
            item['title'] = 'Total Applied Jobs'
            item['value'] = total_jobs_applied.count()
            item['description'] = '21% INCREASE from last month'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-2)
            months = []
            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                dec = dec + relativedelta(months=-1)
            apps_by_month = total_jobs_applied.filter(apply_date__range=[
                last_year, today]).values('apply_date__year', 'apply_date__month').annotate(
                count=Count('pk'))

            serie = {'name': item['title'], 'type': 'line'}
            data = [0] * 12
            for j in range(0, 12):
                count = apps_by_month.filter(
                    apply_date__year=months[j].year, apply_date__month=months[j].month)
                if count.count() > 0:
                    data[j] = count[0]['count']
            serie['data'] = data
            item['graph']['series'].append(serie)
        elif graph == 3:
            item['graph'] = {}
            item['graph']['type'] = 'line'
            item['graph']['series'] = []
            item['title'] = 'Total Rejected Jobs'
            item['value'] = str(total_jobs_applied.filter(is_rejected=True).count()) + '/' + str(
                total_jobs_applied.count())
            item['description'] = '3% DECREASE from last month'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-2)
            months = []
            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                dec = dec + relativedelta(months=-1)
            apps_by_month = total_jobs_applied.filter(apply_date__range=[
                last_year, today], is_rejected=True).values('apply_date__year', 'apply_date__month').annotate(
                count=Count('pk'))

            serie = {'name': item['title'], 'type': 'line'}
            data = [0] * 12
            for j in range(0, 12):
                count = apps_by_month.filter(
                    rejected_date__year=months[j].year, rejected_date__month=months[j].month)
                if count.count() > 0:
                    data[j] = count[0]['count']
            serie['data'] = data
            item['graph']['series'].append(serie)
        response.append(item)
    return JsonResponse(create_response(data=response), safe=False)


@csrf_exempt
@api_view(["GET"])
def detailed(request):
    response = []
    for graph in range(4):
        item = {}
        if graph == 0:
            item['graph'] = {}
            item['graph']['type'] = 'bar'
            item['graph']['series'] = []
            item['graph']['title'] = 'Monthly Applications'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Job Sources'

            system_sources = Source.objects.filter(system=True)
            sources = ['Others']
            for s in system_sources:
                sources.insert(0, s.value)
            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-1)
            months = []
            months_string = []

            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
                months_string.insert(0, d.strftime("%B"))
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                months_string.insert(0, dec.strftime("%B"))
                dec = dec + relativedelta(months=-1)
            for i in sources:
                if i != 'Others':
                    apps = JobApplication.objects.filter(user=request.user, app_source__value=i,
                                                         apply_date__range=[
                                                             last_year, today], is_deleted=False)
                    apps_by_months = apps.values(
                        'apply_date__year', 'apply_date__month').annotate(count=Count('pk'))
                else:
                    apps = JobApplication.objects.filter(user=request.user, app_source__system=False,
                                                         apply_date__range=[
                                                             last_year, today], is_deleted=False)
                    apps_by_months = apps.values(
                        'apply_date__year', 'apply_date__month').annotate(count=Count('pk'))
                item['list']['data'].append({'id': i, 'value': apps.count()})
                serie = {'name': i}
                data = [0] * 12
                for j in range(0, 12):
                    count = apps_by_months.filter(
                        apply_date__year=months[j].year, apply_date__month=months[j].month)
                    if len(count) > 0:
                        data[j] = count[0]['count']
                serie['data'] = data
                serie['type'] = "bar"
                serie['stack'] = 'Source'
                item['graph']['series'].append(serie)

            item['list']['data'].sort(key=lambda x: x['value'], reverse=True)
            item['list']['total'] = JobApplication.objects.filter(user=request.user, apply_date__range=[
                last_year, today], is_deleted=False).count()
            item['graph']['xAxis'] = months_string
        elif graph == 1:
            item['graph'] = {}
            item['graph']['type'] = 'line'
            item['graph']['series'] = []
            item['graph']['title'] = 'Status Change'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Job Statuses'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-1)
            months = []
            months_string = []

            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
                months_string.insert(0, d.strftime("%B"))
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                months_string.insert(0, dec.strftime("%B"))
                dec = dec + relativedelta(months=-1)

            statuses = list(ApplicationStatus.objects.all())
            status_total = ApplicationStatus(value='Total')
            statuses.append(status_total)
            for status in statuses:
                if status.value == 'Total':
                    apps = JobApplication.objects.filter(user=request.user, apply_date__range=[last_year, today],
                                                         is_deleted=False)
                else:
                    apps = JobApplication.objects.filter(user=request.user, application_status=status,
                                                         apply_date__range=[
                                                             last_year, today], is_deleted=False)
                    item['list']['data'].append({'id': status.value.upper(), 'value': apps.count()})
                apps = apps.values(
                    'apply_date__year', 'apply_date__month').annotate(count=Count('pk'))
                serie = {'name': status.value.upper()}
                data = [0] * 12
                for j in range(0, 12):
                    count = apps.filter(
                        apply_date__year=months[j].year, apply_date__month=months[j].month)
                    if len(count) > 0:
                        data[j] = count[0]['count']
                serie['data'] = data
                serie['type'] = "line"
                item['graph']['series'].append(serie)
            item['list']['data'].sort(key=lambda x: x['value'], reverse=True)
            item['list']['total'] = JobApplication.objects.filter(user=request.user, apply_date__range=[
                last_year, today], is_deleted=False).count()
            item['graph']['xAxis'] = months_string
        elif graph == 2:
            item['graph'] = {}
            item['graph']['type'] = 'radar'
            item['graph']['polar'] = []
            item['graph']['series'] = []
            item['graph']['title'] = 'Skill Analysis'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Skills'

            # dummy data
            serie = {'value': [9, 8, 9, 7, 5, 3], 'name': 'Market Demand'}
            item['graph']['series'].append(serie)
            serie = {'value': [10, 8, 5, 7, 3, 2], 'name': 'Your Skills'}
            item['graph']['series'].append(serie)
            indicators = []
            indicator = {'text': 'Java', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'Python', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'R', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'React Native', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'GO', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'React', 'max': 10}
            indicators.append(indicator)
            item['graph']['polar'].append({'indicator': indicators})

            item['list']['data'].append({'id': 'GO', 'value': 27})
            item['list']['data'].append({'id': 'Java', 'value': 18})
            item['list']['data'].append({'id': 'React', 'value': 16})
            item['list']['data'].append({'id': 'R', 'value': 14})
            item['list']['data'].append({'id': 'Python', 'value': 12})
            item['list']['data'].append({'id': 'React Native', 'value': 8})

            item['list']['total'] = 32
        elif graph == 3:
            item['graph'] = {}
            item['graph']['type'] = 'bar'
            item['graph']['series'] = []
            item['graph']['title'] = 'Top Companies'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Companies'

            item['graph']['xAxis'] = []

            top_companies = JobApplication.objects.filter(~Q(application_status=None), user=request.user,
                                                          is_deleted=False).values(
                company=F('company_object__company')).annotate(count=Count('company_object')).order_by('-count')
            if top_companies.count() > 10:
                top_companies = top_companies[:10]

            total = 0
            for company in top_companies:
                item['list']['data'].append({'id': company['company'], 'value': company['count']})
                total += company['count']
            item['list']['total'] = total

            statuses = ApplicationStatus.objects.all()
            for status in statuses:
                item['graph']['xAxis'].append(status.value.upper())
            for company in top_companies:
                serie = {'name': company['company'], 'type': "bar", 'stack': 'Company'}
                data = [0] * statuses.count()
                for idx, status in enumerate(statuses):
                    data[idx] = JobApplication.objects.filter(~Q(application_status=None), user=request.user,
                                                              company_object__company=company['company'],
                                                              application_status=status).count()
                serie['data'] = data
                item['graph']['series'].append(serie)

        response.append(item)
    return JsonResponse(create_response(data=response), safe=False)


@csrf_exempt
@api_view(["GET"])
def agg_detailed(request):
    response = []
    user_profile = request.user
    User = get_user_model()
    filter_by_college = False
    public = get_boolean_from_request(request, 'public')
    student = get_boolean_from_request(request, 'student')
    if user_profile.user_type.name == 'Student' and not public:
        college_users = User.objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, user_type__name__iexact='Student', is_demo=False)])
        filter_by_college = True
    elif user_profile.user_type.name == 'Alumni' and not public:
        college_users = User.objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, user_type__name__iexact='Alumni', is_demo=False)])
        filter_by_college = True
    elif user_profile.user_type.name == 'Career Service' and public:
        college_users = User.objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, is_demo=False)])
        filter_by_college = True
    elif user_profile.user_type.name == 'Career Service' and student:
        college_users = User.objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, user_type__name__iexact='Student',
                                                      is_demo=False)])
        filter_by_college = True
    elif user_profile.user_type.name == 'Career Service' and not student:
        college_users = User.objects.filter(
            id__in=[p.id for p in
                    User.objects.filter(college=user_profile.college, user_type__name__iexact='Alumni', is_demo=False)])
        filter_by_college = True

    if not user_profile.user_type.college_specific_metrics_enabled and not public:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                            safe=False)

    for graph in range(4):
        item = {}
        if graph == 0:
            item['graph'] = {}
            item['graph']['type'] = 'bar'
            item['graph']['series'] = []
            item['graph']['title'] = 'Top Companies Applied'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Companies Applied'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-1)
            months = []
            months_string = []

            if filter_by_college:
                distinct_jobapps = JobApplication.objects.filter(user__in=college_users).distinct('company_object', 'user')
            else:
                distinct_jobapps = JobApplication.objects.filter(user__is_demo=False).distinct('company_object', 'user')
            #  ~Q(application_status__pk = 2) indicates not 'To Apply' statuses in the prod DB.
            top_companies = JobApplication.objects.filter(~Q(application_status=None), ~Q(application_status__pk=2),
                                                          apply_date__range=[
                                                              last_year, today],
                                                          is_deleted=False).values(
                company=F('company_object__company')).annotate(count=Count('company_object')).filter(
                id__in=distinct_jobapps).order_by('-count')

            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
                months_string.insert(0, d.strftime("%B"))
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                months_string.insert(0, dec.strftime("%B"))
                dec = dec + relativedelta(months=-1)

            item['graph']['xAxis'] = months_string

            if top_companies.count() > 10:
                top_companies = top_companies[:10]

            total = 0
            for company in top_companies:
                serie = {'name': company['company'], 'type': 'bar'}
                data = [0] * 12
                for j in range(0, 12):
                    count = JobApplication.objects.filter(company_object__company=company['company'],
                                                          apply_date__year=months[j].year,
                                                          apply_date__month=months[j].month,
                                                          is_deleted=False,
                                                          id__in=distinct_jobapps)
                    data[j] = count.count()
                serie['data'] = data
                serie['stack'] = 'Company'
                item['graph']['series'].append(serie)
                item['list']['data'].append({'id': company['company'], 'value': company['count']})
                total += company['count']
            item['list']['total'] = total

        elif graph == 1:
            item['graph'] = {}
            item['graph']['type'] = 'line'
            item['graph']['series'] = []
            item['graph']['title'] = 'Peak Season'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Peak Season'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-1)
            months = []
            months_string = []

            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
                months_string.insert(0, d.strftime("%B"))
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                months_string.insert(0, dec.strftime("%B"))
                dec = dec + relativedelta(months=-1)

            item['graph']['xAxis'] = months_string

            system_sources = Source.objects.filter(system=True)
            sources = ['Others', 'Total']
            for s in system_sources:
                sources.insert(0, s.value)

            for i in sources:
                if i == 'Total':
                    if filter_by_college:
                        apps = JobApplication.objects.filter(user__in=college_users, apply_date__range=[last_year, today],
                                                             is_deleted=False)
                    else:
                        apps = JobApplication.objects.filter(apply_date__range=[last_year, today], is_deleted=False, user__is_demo=False)
                    apps_by_months = apps.values(
                        'apply_date__year', 'apply_date__month').annotate(count=Count('pk'))
                elif i != 'Others':
                    if filter_by_college:
                        apps = JobApplication.objects.filter(user__in=college_users, app_source__value=i,
                                                         apply_date__range=[
                                                             last_year, today], is_deleted=False)
                    else:
                        apps = JobApplication.objects.filter(app_source__value=i, apply_date__range=[
                                                                 last_year, today], is_deleted=False, user__is_demo=False)
                    apps_by_months = apps.values(
                        'apply_date__year', 'apply_date__month').annotate(count=Count('pk'))
                else:
                    if filter_by_college:
                        apps = JobApplication.objects.filter(user__in=college_users, app_source__system=False,
                                                         apply_date__range=[
                                                             last_year, today], is_deleted=False)
                    else:
                        apps = JobApplication.objects.filter(app_source__system=False, apply_date__range=[
                                                                 last_year, today], is_deleted=False, user__is_demo=False)
                    apps_by_months = apps.values(
                        'apply_date__year', 'apply_date__month').annotate(count=Count('pk'))

                serie = {'name': i}
                data = [0] * 12
                for j in range(0, 12):
                    count = apps_by_months.filter(
                        apply_date__year=months[j].year, apply_date__month=months[j].month)
                    if len(count) > 0:
                        data[j] = count[0]['count']
                serie['data'] = data
                serie['type'] = "line"
                # serie['stack'] = 'Source'
                item['graph']['series'].append(serie)

            total = 0
            for idx, month in enumerate(months):
                if filter_by_college:
                    apps = JobApplication.objects.filter(user__in=college_users, apply_date__year=month.year,
                                                         apply_date__month=month.month,
                                                         is_deleted=False)
                else:
                    apps = JobApplication.objects.filter(apply_date__year=month.year, apply_date__month=month.month,
                                                         is_deleted=False, user__is_demo=False)
                item['list']['data'].append(
                    {'id': months_string[idx] + ' ' + str(month.year), 'value': apps.count()})
                total += apps.count()
            item['list']['data'].sort(key=lambda x: x['value'], reverse=True)
            item['list']['total'] = total
        elif graph == 2:
            item['graph'] = {}
            item['graph']['type'] = 'radar'
            item['graph']['polar'] = []
            item['graph']['series'] = []
            item['graph']['title'] = 'Skill Analysis'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Skills'

            # dummy data
            serie = {'value': [9, 8, 9, 7, 5, 3], 'name': 'Market Demand'}
            item['graph']['series'].append(serie)
            serie = {'value': [10, 8, 5, 7, 3, 2], 'name': 'Overall Skills'}
            item['graph']['series'].append(serie)
            indicators = []
            indicator = {'text': 'Java', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'Python', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'R', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'React Native', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'GO', 'max': 10}
            indicators.append(indicator)
            indicator = {'text': 'React', 'max': 10}
            indicators.append(indicator)
            item['graph']['polar'].append({'indicator': indicators})

            item['list']['data'].append({'id': 'Java', 'value': 27})
            item['list']['data'].append({'id': 'GO', 'value': 18})
            item['list']['data'].append({'id': 'React', 'value': 16})
            item['list']['data'].append({'id': 'R', 'value': 14})
            item['list']['data'].append({'id': 'Python', 'value': 12})
            item['list']['data'].append({'id': 'React Native', 'value': 8})

            item['list']['total'] = 32
        elif graph == 3:
            item['graph'] = {}
            item['graph']['type'] = 'bar'
            item['graph']['series'] = []
            item['graph']['title'] = 'Top Positions Applied'
            item['list'] = {}
            item['list']['data'] = []
            item['list']['title'] = 'Top Positions Applied'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-1)
            months = []
            months_string = []

            if filter_by_college:
                distinct_positions = JobApplication.objects.filter(user__in=college_users).distinct('position', 'user')
            else:
                distinct_positions = JobApplication.objects.filter(user__is_demo=False).distinct('position', 'user')
            #  ~Q(application_status__pk = 2) indicates not 'To Apply' statuses in the prod DB.
            top_positions = JobApplication.objects.filter(~Q(application_status=None), ~Q(application_status__pk=2),
                                                          apply_date__range=[
                                                              last_year, today],
                                                          is_deleted=False).values(
                position_=F('position__job_title')).annotate(count=Count('position')).filter(
                id__in=distinct_positions).order_by('-count').order_by('-count')

            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
                months_string.insert(0, d.strftime("%B"))
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                months_string.insert(0, dec.strftime("%B"))
                dec = dec + relativedelta(months=-1)

            item['graph']['xAxis'] = months_string

            if top_positions.count() > 10:
                top_positions = top_positions[:10]

            total = 0
            for position in top_positions:
                serie = {'name': position['position_'], 'type': 'bar'}
                data = [0] * 12
                for j in range(0, 12):
                    count = JobApplication.objects.filter(~Q(application_status=None), ~Q(application_status__pk=2),
                                                          position__job_title=position['position_'],
                                                          apply_date__year=months[j].year,
                                                          apply_date__month=months[j].month,
                                                          is_deleted=False,
                                                          id__in=distinct_positions)
                    data[j] = count.count()
                serie['data'] = data
                item['graph']['series'].append(serie)
                serie['stack'] = 'Company'
                item['list']['data'].append({'id': position['position_'], 'value': position['count']})
                total += position['count']
            item['list']['total'] = total

        response.append(item)
    return JsonResponse(create_response(data=response), safe=False)


@csrf_exempt
@api_view(["GET"])
def agg_generic(request):
    response = []
    user_profile = request.user
    User = get_user_model()
    filter_by_college = False
    public = get_boolean_from_request(request, 'public')
    student = get_boolean_from_request(request, 'student')
    if user_profile.user_type.name == 'Student' and not public:
        college_users = get_user_model().objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, user_type__name__iexact='Student', is_demo=False)])
        filter_by_college = True
        total_jobs_applied = JobApplication.objects.filter(user__in=college_users, user__is_demo=False, is_deleted=False)
    elif user_profile.user_type.name == 'Alumni' and not public:
        college_users = get_user_model().objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, user_type__name__iexact='Alumni', is_demo=False)])
        filter_by_college = True
        total_jobs_applied = JobApplication.objects.filter(user__in=college_users, user__is_demo=False, is_deleted=False)
    elif user_profile.user_type.name == 'Career Service' and public:
        college_users = get_user_model().objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, is_demo=False)])
        filter_by_college = True
        total_jobs_applied = JobApplication.objects.filter(user__in=college_users, user__is_demo=False,
                                                           is_deleted=False)
    elif user_profile.user_type.name == 'Career Service' and student:
        college_users = get_user_model().objects.filter(
            id__in=[p.id for p in User.objects.filter(college=user_profile.college, user_type__name__iexact='Student',
                                                      is_demo=False)])
        filter_by_college = True
        total_jobs_applied = JobApplication.objects.filter(user__in=college_users, user__is_demo=False,
                                                           is_deleted=False)
    elif user_profile.user_type.name == 'Career Service' and not student:
        college_users = get_user_model().objects.filter(
            id__in=[p.id for p in
                    User.objects.filter(college=user_profile.college, user_type__name__iexact='Alumni', is_demo=False)])
        filter_by_college = True
        total_jobs_applied = JobApplication.objects.filter(user__in=college_users, user__is_demo=False,
                                                           is_deleted=False)
    else:
        if not user_profile.user_type.college_specific_metrics_enabled and not public:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user), safe=False)
        total_jobs_applied = JobApplication.objects.filter(is_deleted=False, user__is_demo=False)
    for graph in range(4):
        item = dict(graph={})
        if graph == 0:
            item['graph']['type'] = 'pie'
            item['graph']['legend'] = []
            item['graph']['series'] = []
            item['title'] = 'Phone Screen Rate'
            if total_jobs_applied.count() == 0:
                item['value'] = '0%'
            else:
                item['value'] = str(round(total_jobs_applied.filter(
                    application_status__value='PHONE SCREEN').count() / total_jobs_applied.count() * 100, 2)) + '%'
            item['description'] = '13% INCREASE from last month'
            statuses = total_jobs_applied.filter(~Q(application_status=None)).values(
                'application_status').annotate(count=Count('pk'))
            for status in statuses:
                status_text = ApplicationStatus.objects.get(
                    pk=status['application_status']).value.upper()
                item['graph']['legend'].append(status_text)
                serie = {'name': status_text, 'value': status['count']}
                if status_text == 'PHONE SCREEN':
                    serie['selected'] = True
                item['graph']['series'].append(serie)
        elif graph == 1:
            item['graph']['type'] = 'pie'
            item['graph']['legend'] = []
            item['graph']['series'] = []
            item['title'] = 'Onsite Interview Rate'
            if total_jobs_applied.count() == 0:
                item['value'] = '0%'
            else:
                item['value'] = str(round(total_jobs_applied.filter(
                    application_status__value='ONSITE INTERVIEW').count() / total_jobs_applied.count() * 100, 2)) + '%'
            item['description'] = '4% DECREASE from last month'
            statuses = total_jobs_applied.filter(~Q(application_status=None)).values(
                'application_status').annotate(count=Count('pk'))
            for status in statuses:
                status_text = ApplicationStatus.objects.get(
                    pk=status['application_status']).value.upper()
                item['graph']['legend'].append(status_text)
                serie = {'name': status_text, 'value': status['count']}
                if status_text == 'ONSITE INTERVIEW':
                    serie['selected'] = True
                item['graph']['series'].append(serie)
        elif graph == 2:
            item['graph']['type'] = 'line'
            item['graph']['series'] = []
            item['title'] = 'Total Applied Jobs'
            item['value'] = total_jobs_applied.count()
            item['description'] = '21% INCREASE from last month'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-2)
            months = []
            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                dec = dec + relativedelta(months=-1)
            apps_by_month = total_jobs_applied.filter(apply_date__range=[
                last_year, today]).values('apply_date__year', 'apply_date__month').annotate(
                count=Count('pk'))

            serie = {'name': item['title'], 'type': 'line'}
            data = [0] * 12
            for j in range(0, 12):
                count = apps_by_month.filter(
                    apply_date__year=months[j].year, apply_date__month=months[j].month)
                if count.count() > 0:
                    data[j] = count[0]['count']
            serie['data'] = data
            item['graph']['series'].append(serie)
        elif graph == 3:
            item['graph']['type'] = 'line'
            item['graph']['series'] = []
            item['title'] = 'Total Users'
            User = get_user_model()
            if filter_by_college:
                total_user = college_users
            else:
                total_user = User.objects.filter(is_demo=False)
            total_user_count = total_user.count()
            item['value'] = total_user_count
            total_application = total_jobs_applied.count()
            total_average = total_application / total_user_count
            item['description'] = 'Average ' + str(round(total_average, 2)) + ' & ' + 'Total ' + str(
                total_application) + ' Jobs'

            today = datetime.date.today() + relativedelta(days=+1)
            last_year = datetime.date.today() + relativedelta(years=-2)
            months = []
            for i in range(0, today.month):
                d = today + relativedelta(months=-1 * i)
                months.insert(0, d)
            dec = today + relativedelta(months=-1 * today.month)
            while len(months) != 12:
                months.insert(0, dec)
                dec = dec + relativedelta(months=-1)
            apps_by_month = total_user.filter(date_joined__range=[
                last_year, today]).values('date_joined__year', 'date_joined__month').annotate(
                count=Count('pk'))

            serie = {'name': item['title'], 'type': 'line'}
            data = [0] * 12
            for j in range(0, 12):
                count = apps_by_month.filter(
                    date_joined__year=months[j].year, date_joined__month=months[j].month)
                if count.count() > 0:
                    if j == 0:
                        data[j] = count[0]['count']
                    else:
                        data[j] = data[j - 1] + count[0]['count']
            serie['data'] = data
            item['graph']['series'].append(serie)
        response.append(item)
    return JsonResponse(create_response(data=response), safe=False)
