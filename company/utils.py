from company.models import Company
from utils.clearbit_company_checker import get_company_detail
import os
from background_task import background
import requests, json
from utils.logger import log


def get_or_create_company(name):
    cd = get_company_detail(name)
    if cd is None:
        company_title = name
    else:
        company_title = cd['name']
    jc = Company.objects.all().filter(cb_name__iexact=company_title)
    if jc.count() == 0:
        # if company doesnt exist save it
        if cd is None:
            jc = Company(company=name, company_logo=None,
                         cb_name=name, cb_company_logo=None, cb_domain=None)
        else:
            jc = Company(company=name, company_logo=None,
                         cb_name=cd['name'], cb_company_logo=cd['logo'], cb_domain=cd['domain'])
        jc.save()
    else:
        jc = jc[0]
    if jc.location_address is None:
        fetch_company_location(jc)
    return jc


@background(schedule=3)
def fetch_company_location(company):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    api_key = os.environ.get('JOBHAX_BACKEND_MAPS_API_KEY', '')
    if api_key is not '':
        query = company.company
        log('Looking location of ' + query, 'e')
        if query is None:
            query = company.cb_name
        if query is not None:
            r = requests.get(url + 'query=' + query +
                             '&key=' + api_key)
            x = r.json()
            y = x['results']
            for i in range(len(y)):
                place = y[i]
                if 'establishment' in place['types']:
                    lat = place['geometry']['location']['lat']
                    lng = place['geometry']['location']['lng']
                    formatted_address = place['formatted_address']
                    company.location_lat = lat
                    company.location_lon = lng
                    company.location_address = formatted_address
                    company.save()
                    break
