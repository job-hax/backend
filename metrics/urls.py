from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from metrics import views

urlpatterns = [
    path('personal/generic/', views.generic, name='personal/generic'),
    path('personal/detailed/', views.detailed, name='personal/detailed'),
    path('aggregated/generic/', views.agg_generic, name='aggregated/generic'),
    path('aggregated/detailed/', views.agg_detailed, name='aggregated/detailed'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
