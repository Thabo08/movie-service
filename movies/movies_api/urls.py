from django.urls import path

from . import views

urlpatterns = [
    path('movies/', views.actor_movies, name='actor_movies'),
]
