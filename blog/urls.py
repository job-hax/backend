from django.urls import path

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
