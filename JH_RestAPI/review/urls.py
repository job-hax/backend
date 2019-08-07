from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from review import views

urlpatterns = [
    path('add_or_update', views.add_or_update_review, name='add_or_update'),
    path('get_reviews', views.get_reviews, name='get_reviews'),
    path('get_source_types', views.get_source_types, name='get_source_types'),
]
urlpatterns = format_suffix_patterns(urlpatterns)