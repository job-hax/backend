from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from blog import views

urlpatterns = [
    path('', views.blogs),
    path('<int:blog_pk>/',
        views.blog),
    path('<int:blog_pk>/upvote/',
        views.upvote),
    path('<int:blog_pk>/downvote/',
        views.downvote),
    path('<int:blog_pk>/view/',
        views.view),
]