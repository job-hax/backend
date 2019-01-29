from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from users import views

urlpatterns = [
    path('auth_social_user', views.auth_social_user, name='auth_social_user'),
    path('sync_user_emails', views.sync_user_emails, name='sync_user_emails'),
    path('update_gmail_token', views.update_gmail_token, name='update_gmail_token'),
]
urlpatterns = format_suffix_patterns(urlpatterns)