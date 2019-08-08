from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from position import views

urlpatterns = [
    path('', views.positions),
]
urlpatterns = format_suffix_patterns(urlpatterns)
