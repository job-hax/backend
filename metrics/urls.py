from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from metrics import views

urlpatterns = [
    path('companyLocations/', views.company_locations),
    path('personal/generic/', views.generic),
    path('personal/detailed/', views.detailed),
    path('aggregated/generic/', views.agg_generic),
    path('aggregated/detailed/', views.agg_detailed),
]
urlpatterns = format_suffix_patterns(urlpatterns)
