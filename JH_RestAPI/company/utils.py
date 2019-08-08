from company.models import Company
from utils.clearbit_company_checker import get_company_detail


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
    return jc