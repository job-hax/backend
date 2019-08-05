from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from college import views

urlpatterns = [
    path('', views.get_colleges),
    path('majors', views.get_majors),
]
urlpatterns = format_suffix_patterns(urlpatterns)
