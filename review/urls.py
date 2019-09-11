from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from review import views

urlpatterns = [
    path('', views.reviews),
    path('sourceTypes/', views.source_types),
    path('employmentAuthorizations/', views.employment_authorizations),
]
urlpatterns = format_suffix_patterns(urlpatterns)
