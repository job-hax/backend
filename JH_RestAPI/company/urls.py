from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from company import views

urlpatterns = [
    path('', views.get_companies),
    path('<int:company_pk>/positions/',
        views.get_company_positions),
]
urlpatterns = format_suffix_patterns(urlpatterns)
