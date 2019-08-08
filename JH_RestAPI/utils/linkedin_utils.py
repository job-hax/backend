import json
import os
import traceback

import requests
from bs4 import BeautifulSoup as bs

from utils.logger import log
from .gmail_utils import find_nth


def parse_job_detail(body):
    """Parse html body and get job posting details
    Args:
      body: email html body
    Returns:
      String values which represent details of job post in JSON format.
    """
    try:
        link = body[find_nth(body, 'https://www.linkedin.com/comm/jobs/view/', 1): find_nth(body, '?trk', 1)]
        url = requests.get(link)
        htmltext = url.text
        s = find_nth(htmltext, '<code id="viewJobMetaTagModule">', 1)
        e = htmltext.rfind('--></code>') + 10
        plainData = htmltext[s: e]
        plainData = plainData.replace('<!--', '')
        plainData = plainData.replace('-->', '')
        soup = bs(plainData, "html.parser")
        try:
            posterInformation = soup.find('code', id='posterInformationModule')
            posterInformationJSON = posterInformation.getText()
        except:
            posterInformationJSON = '{}'
        try:
            decoratedJobPosting = soup.find('code', id='decoratedJobPostingModule')
            decoratedJobPostingJSON = decoratedJobPosting.getText()
        except:
            decoratedJobPostingJSON = '{}'
        try:
            topCardV2 = soup.find('code', id='topCardV2Module')
            topCardV2JSON = topCardV2.getText()
        except:
            topCardV2JSON = '{}'

        return posterInformationJSON, decoratedJobPostingJSON, topCardV2JSON
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return '{}', '{}', '{}'


def get_access_token_with_code(code):
    try:
        post_data = {'grant_type': 'authorization_code', 'code': code,
                     'redirect_uri': 'http://localhost:8080/action-linkedin-oauth2',
                     'client_id': os.environ['JOBHAX_LINKEDIN_CLIENT_KEY'],
                     'client_secret': os.environ['JOBHAX_LINKEDIN_CLIENT_SECRET']}
        log(post_data, 'e')
        response = requests.post('https://www.linkedin.com/uas/oauth2/accessToken',
                                 data=post_data, headers={'content-type': 'application/x-www-form-urlencoded'})
        jsonres = json.loads(response.text)
        log(jsonres, 'e')
        return jsonres['access_token']
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return None
