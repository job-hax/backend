from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from alumni import views

urlpatterns = [
    path('', views.alumni),
    path('majors/',
         views.majors),
    path('companies/',
         views.companies),
    path('positions/',
         views.positions),
]
urlpatterns = format_suffix_patterns(urlpatterns)
