from django.urls import path
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

from jobapps import views

urlpatterns = [
    path('get_statuses', views.get_statuses, name='get_statuses'),
    path('get_status_history', views.get_status_history, name='get_status_history'),
    path('get_jobapps', views.get_jobapps, name='get_jobapps'),
    path('update_jobapp', views.update_jobapp, name='update_jobapp'),
    path('edit_jobapp', views.edit_jobapp, name='edit_jobapp'),
    path('add_jobapp', views.add_jobapp, name='add_jobapp'),
    path('delete_jobapp', views.delete_jobapp, name='delete_jobapp'),
    path('get_jobapp_notes', views.get_jobapp_notes, name='get_jobapp_notes'),
    path('update_jobapp_note', views.update_jobapp_note, name='update_jobapp_note'),
    path('delete_jobapp_note', views.delete_jobapp_note, name='delete_jobapp_note'),
    path('add_jobapp_note', views.add_jobapp_note, name='add_jobapp_note'),
    path('get_sources', views.get_sources, name='get_sources'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
