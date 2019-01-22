from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from jobapps import views

urlpatterns = [
    path('get_statuses', views.get_statuses, name='get_statuses'),
    path('get_jobapps', views.get_jobapps, name='get_jobapps'),
]
urlpatterns = format_suffix_patterns(urlpatterns)