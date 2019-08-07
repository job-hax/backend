from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from utils import views

urlpatterns = [
    path('agreements/', views.agreements),
    path('countries/', views.countries),
    path('countries/<int:country_pk>/states/',
        views.states),
]
urlpatterns = format_suffix_patterns(urlpatterns)
