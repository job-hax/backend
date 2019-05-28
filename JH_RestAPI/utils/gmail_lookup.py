from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient import errors
from users.models import Profile
import string
from datetime import datetime
import requests
import traceback
from bs4 import BeautifulSoup as bs

from .social_auth_credentials import Credentials

from jobapps.models import JobApplication
from jobapps.models import GoogleMail
from jobapps.models import ApplicationStatus
from jobapps.models import StatusHistory
from jobapps.models import Source
from position.models import JobPosition
from company.models import Company
from utils.clearbit_company_checker import get_company_detail
import base64
from .gmail_utils import convertTime
from .gmail_utils import removeHtmlTags
from .gmail_utils import find_nth
from .gmail_utils import unicodetoascii
from utils.logger import log


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
        if JobApplication.objects.all().filter(msgId=msg_id).count() > 0:
            log('this email parsed before', 'e')
            return
        message = service.users().messages().get(
            userId=user_id, id=msg_id, format='full').execute()
        mail_from = None
        mail_subject = None
        mail_body = None
        original_date = None
        for header in message['payload']['headers']:
            if header['name'] == 'Subject':
                mail_subject = str(header['value'])
                if mail_from is not None and original_date is not None:
                    break
            elif header['name'] == 'From':
                mail_from = str(header['value'])
                if mail_subject is not None and original_date is not None:
                    break
            elif header['name'] == 'Date':
                date = header['value']
                original_date = header['value']
                date = convertTime(str(date))
        if 'parts' not in message['payload']:
            if message['payload']['mimeType'] == 'text/html' and int(message['payload']['body']['size']) > 0:
                mail_body = str(base64.urlsafe_b64decode(
                    message['payload']['body']['data'].encode('ASCII')))
            else:
                mail_body = None
        else:
            for part in message['payload']['parts']:
                if (part['mimeType'] == 'text/html'):
                    # get mail's body as a string
                    mail_body = str(base64.urlsafe_b64decode(
                        part['body']['data'].encode('ASCII')))
                    break
                else:
                    mail_body = None

        if original_date is None:
            log(mail_subject, 'e')
            log(str(message['payload']['headers']), 'e')

        if mail_subject is not None and mail_body is not None and original_date is not None:
            inserted_before = GoogleMail.objects.all().filter(msgId=msg_id)
            if inserted_before.count() == 0:
                app_source = Source.objects.get(value__iexact=source)
                mail = GoogleMail(user=user, subject=mail_subject, body=mail_body, date=date, msgId=msg_id,
                                  app_source=app_source)
                mail.save()
            else:
                mail = inserted_before[0]
        else:
            mail = None

        job_title = ''
        company = ''
        image_url = ''

        if source == 'LinkedIn':
            # job_title and company are in the subject in LinkedIn mails
            # we should find them in the subject
            if 'for ' in mail_subject and ' at ' in mail_subject:
                job_title = mail_subject[mail_subject.index(
                    'for ') + 4: mail_subject.index(' at ')]
            if 'at ' in mail_subject:
                company = mail_subject[mail_subject.index('at ') + 3:]

            if mail_body is not None:
                # trying to find company logo in the body
                s = find_nth(mail_body, 'https://media.licdn.com', 2)
                if s != -1:
                    e = find_nth(mail_body, '" alt="' + company + '"', 1)
                    image_url = mail_body[s: e].replace('&amp;', '&')
                    image_exists = requests.get(image_url)
                    if len(image_url) > 300:
                        image_url = None
                    if image_exists.status_code == 404:
                        image_url = None
                else:
                    image_url = None

        elif source == 'Vettery':
            # job_title and company are in the body in Vettery mails
            if mail_body is not None:
                if 'Role: ' in mail_body and 'Salary' in mail_body:
                    job_title = mail_body[mail_body.index(
                        'Role: ') + 6: mail_body.index('Salary')]
                    job_title = removeHtmlTags(job_title)
                if 'interview with ' in mail_body and '. Interested?' in mail_body:
                    company = mail_body[mail_body.index(
                        'interview with ') + 15: mail_body.index('. Interested?')]
                elif 'Our take on ' in mail_body and ':</span>' in mail_body:
                    company = mail_body[mail_body.index(
                        'Our take on ') + 12: mail_body.index(':</span></')]
                image_url = None
        elif source == 'Hired.com':
            # job_title and company are in the body in Hired.com mails
            if 'Request: ' in mail_subject and ' at ' in mail_subject:
                job_title = mail_subject[mail_subject.index(
                    'Request: ') + 9: mail_subject.index(' at ')]
            if 'at ' in mail_subject and '($' in mail_subject:
                company = mail_subject[mail_subject.index(
                    'at ') + 3: mail_subject.index('($')]
            image_url = None
        elif source == 'Indeed':
            # job_title is in the subject
            if 'Indeed Application: ' in mail_subject:
                job_title = mail_subject[mail_subject.index(
                    'Indeed Application: ') + 20:]

            if mail_body is not None:
                # company is in the body
                if 'updates from' in mail_body and '</b>' in mail_body:
                    c_start_index = mail_body.index('updates from') + 16
                    c_end_index = mail_body[c_start_index: (
                        c_start_index + 100)].index('</b>')
                    company = mail_body[c_start_index: c_start_index + c_end_index]
                image_url = None
        elif source == 'glassdoor':
            # company is in the subject
            if 'on to ' in mail_subject and ' completed.' in mail_subject:
                company = mail_subject[mail_subject.index(
                    'on to ') + 6: mail_subject.index(' completed.')]

            if mail_body is not None:
                # job_title is in the body
                soup = bs(mail_body, 'html.parser')
                images = soup.findAll('img')
                for image in images:
                    if image.has_attr('alt') and image['alt'] == company:
                        image_url = image['src']
                        image_exists = requests.get(image_url)
                        if image_exists.status_code == 404:
                            image_url = None
                        break
                job_title = soup.find(
                    'a', attrs={'style': 'text-decoration: none; color:#0066cc'}).contents[0]
        elif source == 'jobvite.com':
            if 'Recruiting Team' in mail_from:
                company = mail_from[:mail_from.find(' Recruiting Team')]
                if ' for ' in mail_subject and ' at ' in mail_subject:
                    job_title = mail_subject[mail_subject.index(
                        ' for ') + 5: mail_subject.index(' at ')]

                if mail_body is not None:
                    # check the body for more accurate companmy name
                    if ' at ' in mail_body and '. We' in mail_body:
                        company = mail_body[mail_body.index(
                            ' at ') + 4:mail_body.index('. We')]

                    # check the body for the job title
                    if ' the ' in mail_body and ' role at ' + company in mail_body:
                        job_title = mail_body[mail_body.index(
                            ' the ') + 5:mail_body.index(' role at ')]
                    elif ' the ' in mail_body and ' job at ' + company in mail_body:
                        job_title = mail_body[mail_body.index(
                            ' the ') + 5:mail_body.index(' job at ')]
            else:
                # jobinvite sends the approval email with this keyword
                return
        elif source == 'smartrecruiters.com':
            company = mail_subject[mail_subject.rindex(
                'applying to ') + 12:].strip(string.punctuation)
            soup = bs(mail_body, 'html.parser')
            ps = soup.findAll('p')
            first_parag = ''
            if len(ps) == 0:
                first_parag = soup.text
            for p in ps:
                if company in p.text:
                    first_parag = p.text
                    break
            if first_parag != '':
                # needs more data to determine the pattern
                if ' position of ' in first_parag and '. We' in first_parag:
                    job_title = first_parag[first_parag.index(
                        ' position of ') + 13:first_parag.index('. We')]
                elif 'application for the ' in first_parag and ', ' + company in first_parag:
                    job_title = first_parag[
                        first_parag.index('application for the ') + 20:first_parag.index(', ' + company)]
        elif source == 'greenhouse.io':
            pass
        elif source == 'lever.co':
            company = mail_from[:mail_from.index(' <no-reply@hire.lever.co>')]
            company = company.replace('"', '')
            if 'application for ' in mail_body and '.&nbsp;</div' in mail_body:
                job_title = mail_body[mail_body.index(
                    "application for ") + 16:mail_body.index(".&nbsp;</div")]
            elif 'application for ' in mail_body and '. Our' in mail_body:
                job_title = mail_body[mail_body.index(
                    "application for ") + 16:mail_body.index(". Our")]
            elif 'application for ' in mail_body and ', and we are d' in mail_body:
                job_title = mail_body[mail_body.index(
                    'application for ') + 16:mail_body.index(', and we are d')]
                job_title = str(unicodetoascii(job_title))
            elif 'application for our ' in mail_body and ' opening' in mail_body:
                job_title = mail_body[mail_body.index(
                    "application for our ") + 20:mail_body.index(" opening")]
            elif 'application for the ' in mail_body and ' role.' in mail_body:
                job_title = mail_body[mail_body.index(
                    "application for the ") + 20:mail_body.index(" role.")]

        elif source == 'ziprecruiter.com':
            soup = bs(mail_body, 'html.parser')
            ps = soup.findAll('b')
            if len(ps) == 2:
                job_title = ps[0].text
                company = ps[1].text

        inserted_before = JobApplication.objects.all().filter(msgId=msg_id)
        if inserted_before.count() == 0 and job_title != '' and company != '':
            # jt is current dummy job title in the db
            jt = JobPosition.objects.all().filter(job_title__iexact=job_title)
            if jt.count() == 0:
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
            if jc.count() == 0:
                # if company doesnt exist save it
                if cd is None:
                    jc = Company(company=company, company_logo=image_url, cb_name=company, cb_company_logo=None,
                                 cb_domain=None)
                else:
                    jc = Company(company=company, company_logo=image_url, cb_name=cd['name'],
                                 cb_company_logo=cd['logo'], cb_domain=cd['domain'])
                jc.save()
            else:
                jc = jc[0]

            if ApplicationStatus.objects.filter(default=True).count() == 0:
                status = ApplicationStatus(value='Applied', default=True)
                status.save()
            else:
                status = ApplicationStatus.objects.get(default=True)
            source = Source.objects.get(value__iexact=source)
            japp = JobApplication(position=jt, companyObject=jc, applyDate=date, msgId=msg_id, app_source=source,
                                  user=user, applicationStatus=status)
            japp.save()
            log('Job Application inserted : ' + str(japp), 'i')
            status_history = StatusHistory(
                job_post=japp, applicationStatus=status)
            status_history.save()
            if mail is not None:
                mail.job_post = japp
                mail.app_source = source
                mail.save()

    except errors.HttpError as error:
        if error.resp.status == 403 or error.resp.status == 401:
            return False
        log('An error occurred: %s' % error, 'e')
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')


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
        log('An error occurred: %s' % error, error)


def fetchJobApplications(user):
    time_string = ''
    # checks user last update time and add it as a query parameter
    profile = Profile.objects.get(user=user)

    if profile.gmail_last_update_time != 0:
        time = profile.gmail_last_update_time - 24 * 60 * 60
        time_string = ' AND after:' + str(time)
        log('its not the first time query will be added : ' + time_string, 'i')
    else:
        log('its the first time.. so we are querying all mails', 'i')

    # initiates Gmail API
    usa = user.social_auth.get(provider='google-oauth2')
    try:
        creds = Credentials(usa)
        GMAIL = build('gmail', 'v1', credentials=creds)
        # retrieves user email's with custom query parameter
        sources = Source.objects.filter(system=True)
        log(str(sources), 'e')
        allMails = {}
        for s in sources:
            mails = get_emails_with_custom_query(
                GMAIL, 'me', s.gmail_key + time_string)
            allMails[s.value] = mails
            # linkedInMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:jobs-listings@linkedin.com AND subject:You applied for' + time_string)# AND after:2018/01/01')
        # hiredMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:reply@hired.com AND subject:Interview Request' + time_string)
        # vetteryMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:@connect.vettery.com AND subject:Interview Request' + time_string)
        # indeedMessages = get_emails_with_custom_query(GMAIL, 'me', 'from:indeedapply@indeed.com AND subject:Indeed Application' + time_string)
        # mails = get_emails_with_custom_query(service, 'me', 'from:notification@jobvite.com AND in:anywhere')
        # mails = get_emails_with_custom_query(service, 'me', 'from:notifications@smartrecruiters.com AND subject:"Thank you for applying to" AND in:anywhere')
        # mails = get_emails_with_custom_query(service, 'me', 'from:no-reply@greenhouse.io and in:anywhere and subject:{"appl" and "for"}')
        # mails = get_emails_with_custom_query(service, 'me', 'from:@hire.lever.co and subject:"Thank" AND in:anywhere')
    except Exception as e:
        log('Users google token probably expired. Should have new token from google', 'e')
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        profile.is_gmail_read_ok = False
        profile.save()
        return

    for m in allMails.values():
        if m is False:
            profile.is_gmail_read_ok = False
            profile.save()
            log('403 error got from Google. Check permissions...', 'e')
            return

    # retvieves specific email's detail one by one
    for s, mails in allMails.items():
        if mails is not None:
            for mail in mails:
                get_email_detail(GMAIL, 'me', mail['id'], user, s)

                # updates user last update time after all this
    now = datetime.utcnow().timestamp()
    profile.gmail_last_update_time = now
    profile.is_gmail_read_ok = True
    profile.save()
