from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from position import views

urlpatterns = [
    path('', views.get_positions),
]
urlpatterns = format_suffix_patterns(urlpatterns)
