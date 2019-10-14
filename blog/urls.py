from django.urls import path

from blog import views

urlpatterns = [
    path('', views.blogs),
    path('stats/', views.stats),
    path('<int:blog_pk>/',
         views.blog),
    path('<int:blog_pk>/vote/',
         views.vote),
    path('<int:blog_pk>/view/',
         views.view),
]
