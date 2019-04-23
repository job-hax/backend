from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from metrics import views

urlpatterns = [
    path('get_total_application_count', views.get_total_application_count, name='get_total_application_count'),
    path('get_application_count_by_month', views.get_application_count_by_month, name='get_application_count_by_month'),
    path('get_application_count_by_month_with_total', views.get_application_count_by_month_with_total, name='get_application_count_by_month_with_total'),
    path('get_count_by_statuses', views.get_count_by_statuses, name='get_count_by_statuses'),
    path('get_word_count', views.get_word_count, name='get_word_count'),
    path('get_count_by_jobtitle_and_statuses', views.get_count_by_jobtitle_and_statuses, name='get_count_by_jobtitle_and_statuses'),
    path('get_top_companies', views.get_top_companies, name='get_top_companies'),
    path('get_top_positions', views.get_top_positions, name='get_top_positions'),
    path('get_statistics', views.get_statistics, name='get_statistics'),
    path('get_monthly_application_count', views.get_monthly_application_count, name='get_monthly_application_count'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
