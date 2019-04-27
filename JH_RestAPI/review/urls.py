from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from review import views

urlpatterns = [
    path('add_or_update', views.add_or_update_review, name='add_or_update'),
    path('get_reviews', views.get_reviews, name='get_reviews'),
]
urlpatterns = format_suffix_patterns(urlpatterns)