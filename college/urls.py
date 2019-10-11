from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from college import views

urlpatterns = [
    path('', views.colleges),
    path('coaches/',
         views.coaches),
    path('homePage/', views.home_page),
]
urlpatterns = format_suffix_patterns(urlpatterns)
