from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from college import views

urlpatterns = [
    path('', views.colleges),
    path('coaches/',
         views.coaches),
    path('homePage/', views.home_page),
    path('landingPage/', views.landing_page),
    path('homePage/videos/', views.home_page_videos),
]
urlpatterns = format_suffix_patterns(urlpatterns)
