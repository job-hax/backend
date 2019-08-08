from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from alumni import views

urlpatterns = [
    path('', views.alumni),
]
urlpatterns = format_suffix_patterns(urlpatterns)
