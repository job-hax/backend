import hashlib
import datetime
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from utils.generic_json_creator import create_response
from utils.logger import log
from utils.error_codes import ResponseCodes
import os
import traceback


def get_boolean_from_request(request, key, method='POST'):
    " gets the value from request and returns it's boolean state "
    value = getattr(request, method).get(key, False)

    if value == 'False' or value == 'false' or value == '0' or value == 0:
        value = False
    elif value:
        value = True
    else:
        value = False

    return value


def generate_activation_key_and_expiredate(username):
    # We generate a random activation key
    activation_key = generate_activation_key(username)
    expiration_time = datetime.datetime.strftime(
        datetime.datetime.now() + datetime.timedelta(hours=2), "%Y-%m-%d %H:%M:%S")
    return activation_key, expiration_time


def generate_activation_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()


def send_email(email, activation_key, action):
    site = settings.SITE_URL
    url = site + '/action?action=' + action + '&code=' + activation_key

    if action == 'activate':
        subject = '[JobHax] Confirm E-mail Address'
        body = '''<html>
						Welcome to JobHax!<br>
						<br>
						You must follow this link to <span class="il">activate</span> your account:<br>
						<a href="''' + url + '''">''' + url + '''</a><br>
						<br>
						Have fun with the JobHax, and don't hesitate to contact us with your feedback.
						</html>'''
    elif action == 'warning':
        subject = '[JobHax] Unusual Activity Detected'
        body = '''<html>
						Welcome to JobHax!<br>
						<br>
						You must follow this link to <span class="il">activate</span> your account:<br>
						Have fun with the JobHax, and don't hesitate to contact us with your feedback.
						</html>'''
    else:
        subject = '[JobHax] Reset your password'
        body = '''<html>
						You recently requested to reset your password.<br>
						<br>
						To reset your password you must follow this link:<br>
						<a href="''' + url + '''">''' + url + '''</a><br>
						<br>
						If you did not make this request, you can safely ignore this email. A password reset request can be made by anyone,
						and it does not indicate that your account is in any danger of being accessed by someone else.
						</html>'''
    email = EmailMessage(subject, body, to=[email])
    email.content_subtype = "html"  # this is the crucial part
    try:
        email.send()
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')


def verify_recaptcha(email, token, action):
    try:
        secret = os.environ['JOBHAX_RECAPTCHA_SECRET']
    except Exception as e:
        log(traceback.format_exception(None, e, e.__traceback__), 'e')
        return ResponseCodes.success
    post_data = {}
    post_data['secret'] = secret
    post_data['response'] = token
    response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                             data=post_data, headers={'content-type': 'application/x-www-form-urlencoded'})
    jsonres = json.loads(response.text)
    if jsonres['success'] == True and jsonres['action'] == action and jsonres['score'] > 0.5:
        return ResponseCodes.success
    else:
        log(jsonres, "e")
        # if email is not None:
        #    send_email(email, "", "warning")
        return ResponseCodes.verify_recaptcha_failed
