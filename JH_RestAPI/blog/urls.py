from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from blog import views

urlpatterns = [
    path('', views.blogs),
    path('<int:blog_pk>/',
        views.blog),
]