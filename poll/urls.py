from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from poll import views

urlpatterns = [
    path('', views.polls),
    path('<int:poll_pk>/vote/',
         views.vote),
    path('<int:poll_pk>/result/',
         views.result),
]
urlpatterns = format_suffix_patterns(urlpatterns)
