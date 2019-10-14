from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from event import views

urlpatterns = [
    path('', views.events),
    path('stats/', views.stats),
    path('types/', views.types),
    path('<int:event_pk>/',
         views.event),
    path('<int:event_pk>/attend/',
         views.attend),
    path('<int:event_pk>/leave/',
         views.leave),
]
urlpatterns = format_suffix_patterns(urlpatterns)