from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.actor_movies, name='actor_movies'),
]
