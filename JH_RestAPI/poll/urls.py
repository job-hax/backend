from django.conf.urls import url

from poll import views

urlpatterns = [
    url(r'^vote/(?P<poll_pk>\d+)/$', views.vote, name='poll_vote'),
    url(r'^polls/', views.polls, name='polls'),
    url(r'^result/(?P<poll_pk>\d+)/$', views.result, name='poll_result'),
]