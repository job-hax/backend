from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient import errors
from users.models import Profile
import string
from datetime import datetime
import requests

from requests import exceptions as requests_errors

from google.auth.exceptions import RefreshError
from .social_auth_credentials import Credentials
#from google.oauth2.credentials import Credentials
from social_django.utils import load_strategy

from jobapps.models import JobApplication
from jobapps.models import GoogleMail
from jobapps.models import ApplicationStatus
from jobapps.models import JobPostDetail
import base64
import time
from .gmail_utils import convertTime
from .gmail_utils import removeHtmlTags
from .gmail_utils import find_nth
from .linkedin_utils import parse_job_detail

def get_email_detail(service, user_id, msg_id, user, source):
  """Get a Message with given ID.
  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.
  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
    jobTitle = ''
    company = ''
    image_url = ''
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            subject = str(header['value'])
            if(source == 'LinkedIn'):
                jobTitle = subject[subject.index('for ') + 4 : subject.index(' at ')]
                company = subject[subject.index('at ') + 3:]
            elif(source == 'Hired.com'):
                jobTitle = subject[subject.index('Request: ') + 9 : subject.index(' at ')]
                company = subject[subject.index('at ') + 3 : subject.index('($')]
            elif(source == 'Indeed'):
                jobTitle = subject[subject.index('Indeed Application: ') + 20 : ]
        elif header['name'] == 'Date':
            date = header['value']
            original_date = header['value']
            date = convertTime(str(date))
    try:
        if 'parts' not in message['payload']:
            if message['payload']['mimeType'] == 'text/html' and int(message['payload']['body']['size']) > 0:
                body = str(base64.urlsafe_b64decode(message['payload']['body']['data'].encode('ASCII')))
            else:
                body = None
        else:    
            for part in message['payload']['parts']:
                if(part['mimeType'] == 'text/html'):
                    #get mail's body as a string
                    body = str(base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')))
                    break
                else:
                    body = None  
        if body is not None:            
            if(source == 'LinkedIn'):
                posterInformationJSON, decoratedJobPostingJSON, topCardV2JSON = parse_job_detail(body)
                s = find_nth(body, 'https://media.licdn.com', 2)
                if(s != -1):
                    e = find_nth(body, '" alt="' + company + '"', 1)
                    image_url = body[s : e].replace('&amp;', '&')
                    image_exists=requests.get(image_url)
                    if(image_exists.status_code == 404):
                        image_url = None 
                else:
                    image_url = None
                if len(image_url) > 300:
                    image_url = None
            elif(source == 'Vettery'):
                jobTitle = body[body.index('Role: ') + 6 : body.index('Salary')]
                jobTitle = removeHtmlTags(jobTitle)
                company = body[body.index('interview with ') + 15 : body.index('. Interested?')]
                image_url = None
            elif(source == 'Indeed'):
                c_start_index = body.index('updates from') + 16
                c_end_index = body[c_start_index : (c_start_index + 100)].index('</b>')
                company = body[c_start_index : c_start_index + c_end_index]
                image_url = None
            elif(source == 'Hired.com'):
                image_url = None                
    except Exception as e:
        print('exception')
        print(e)
        body = None

    if subject is not None and body is not None and original_date is not None:
        inserted_before = GoogleMail.objects.all().filter(msgId=msg_id)
        print(inserted_before)
        mail = GoogleMail(user=user, subject=subject, body=body, date=date, msgId=msg_id)
        if len(inserted_before) == 0:
            mail.save()
    else:
        mail = None        

    if user.is_authenticated:
      inserted_before = JobApplication.objects.all().filter(msgId=msg_id)
      print(image_url)
      if len(inserted_before) == 0 and jobTitle != '' and company != '':
        if ApplicationStatus.objects.count() == 0:
            status = ApplicationStatus(value='Applied')
            status.save()  
        else:
            status = ApplicationStatus.objects.get(value='Applied')
        japp = JobApplication(jobTitle=jobTitle, company=company, applyDate=date, msgId=msg_id, source = source, user = user, companyLogo = image_url, applicationStatus = status)
        japp.save()
        if(source == 'LinkedIn'):
            japp_details = JobPostDetail(job_post = japp, posterInformation = posterInformationJSON, decoratedJobPosting = decoratedJobPostingJSON, topCardV2 = topCardV2JSON)
            japp_details.save()
        if mail is not None:
            mail.job_post = japp
            mail.save()

  except errors.HttpError as error:
    if error.resp.status == 403 or error.resp.status == 401:
        return False
    print('An error occurred: %s' % error)



def get_emails_with_custom_query(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.
  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.
  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query, includeSpamTrash=True).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token, includeSpamTrash=True).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError as error:
    if error.resp.status == 403 or error.resp.status == 401:
        return False
    print('An error occurred: %s' % error)

def fetchJobApplications(user):
    time_string = ''
    #checks user last update time and add it as a query parameter
    profile = Profile.objects.get(user=user)

    if profile.gmail_last_update_time != 0:
        time_string = ' AND after:' + str(profile.gmail_last_update_time)
        print('its not the first time query will be added : ' + time_string)
    else:
        print('its the first time.. so we are querying all mails')

    #try:
    #initiates Gmail API
    #usa = user.social_auth.get(provider='google-oauth2')
    #cre = Credentials(usa)
    #GMAIL = build('gmail', 'v1', credentials=cre)
    usa = user.social_auth.get(provider='google-oauth2')
    #print(usa.extra_data['access_token'])
    #strategy = load_strategy()
    #usa.refresh_token(strategy)
    #print(usa.extra_data['access_token'])
    try:
        creds= Credentials(usa)
        GMAIL = build('gmail', 'v1', credentials=creds)
        #retrieves user email's with custom query parameter
        linkedInMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:jobs-listings@linkedin.com AND subject:You applied for' + time_string)# AND after:2018/01/01')
        hiredMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:reply@hired.com AND subject:Interview Request' + time_string)
        vetteryMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:@connect.vettery.com AND subject:Interview Request' + time_string)
        indeedMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:indeedapply@indeed.com AND subject:Indeed Application' + time_string)
    except Exception as e:
        print('Users google token probably expired. Should have new token from google')
        print(e)
        profile.is_gmail_read_ok = False
        profile.save()
        return          

    if linkedInMessages is False or hiredMessages is False \
        or indeedMessages is False or vetteryMessages is False:
        profile.is_gmail_read_ok = False
        profile.save()
        print('403 error got from Google. Check permissions...')
        return

    #retvieves specific email's detail one by one
    if linkedInMessages is not None:
        for message in linkedInMessages:
            get_email_detail(GMAIL, 'me', message['id'], user, 'LinkedIn')
    if hiredMessages is not None:
        for message in hiredMessages:
            get_email_detail(GMAIL, 'me', message['id'], user, 'Hired.com')
    if indeedMessages is not None:        
        for message in indeedMessages:
            get_email_detail(GMAIL, 'me', message['id'], user, 'Indeed')
    if vetteryMessages is not None:           
        for message in vetteryMessages:
            get_email_detail(GMAIL, 'me', message['id'], user, 'Vettery')

    #updates user last update time after all this
    now = datetime.utcnow().timestamp()
    profile.gmail_last_update_time = now
    profile.is_gmail_read_ok = True
    profile.save()      
    #except Exception as error:
    #    print('An error occurred: %s' % error)