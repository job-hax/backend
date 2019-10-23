from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from jobapps import views

urlpatterns = [
    path('statuses/', views.statuses),
    path('sources/', views.sources),
    path('', views.job_applications),
    path('<int:job_app_pk>/statusHistory/', views.status_history),
    path('<int:job_app_pk>/notes/', views.notes),
    path('<int:job_app_pk>/files/', views.files),
    path('<int:job_app_pk>/contacts/', views.contacts),
]
urlpatterns = format_suffix_patterns(urlpatterns)
