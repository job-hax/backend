from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from users import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('auth_social_user', views.auth_social_user, name='auth_social_user'),
    path('get_linkedin_profile', views.get_linkedin_profile, name='get_linkedin_profile'),
    path('refresh_token', views.refresh_token, name='refresh_token'),
    path('sync_user_emails', views.sync_user_emails, name='sync_user_emails'),
    path('update_gmail_token', views.update_gmail_token, name='update_gmail_token'),
    path('get_user_google_mails', views.get_user_google_mails, name='get_user_google_mails'),
]
urlpatterns = format_suffix_patterns(urlpatterns)