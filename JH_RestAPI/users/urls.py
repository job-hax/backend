from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from users import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('activate', views.activate_user, name='activate'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('check_forgot_password', views.check_forgot_password,
         name='check_forgot_password'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('generate_activation_code', views.generate_activation_code,
         name='generate_activation_code'),
    path('change_password', views.change_password, name='change_password'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('update_profile_photo', views.update_profile_photo,
         name='update_profile_photo'),
    path('get_employment_statuses', views.get_employment_statuses,
         name='get_employment_statuses'),
    path('get_employment_auths', views.get_employment_auths,
         name='get_employment_auths'),
    path('auth_social_user', views.auth_social_user, name='auth_social_user'),
    path('get_profile', views.get_profile, name='get_profile'),
    path('refresh_token', views.refresh_token, name='refresh_token'),
    path('sync_user_emails', views.sync_user_emails, name='sync_user_emails'),
    path('update_gmail_token', views.update_gmail_token, name='update_gmail_token'),
    path('get_user_google_mails', views.get_user_google_mails,
         name='get_user_google_mails'),
    path('feedback', views.feedback, name='feedback'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
