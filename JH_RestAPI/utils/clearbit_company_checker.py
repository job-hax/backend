import requests
from utils.logger import log
import os

def get_company_detail(name):
    try:
        token = os.environ['JOBHAX_CLEARBIT_KEY']
        r = requests.get('https://company.clearbit.com/v1/domains/find?name=' + name, headers={'Authorization': 'Bearer ' + token})
        data = r.json()
        if 'error' not in data:
            return data
        else:
            return None
    except Exception as e:
        log(e, 'e')  
        return None
