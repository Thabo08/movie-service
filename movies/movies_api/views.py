from django.http import HttpResponse
import requests
import json

from .models import Key
from .movie_requests import test_helper


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def actor_movies(request):
    try:
        key = validate_request(request)
        return test_helper(key)
    except ValueError:
        return HttpResponse('Bad request', 400)


def validate_request(request):
    firstname = request.GET.get('firstname')
    lastname = request.GET.get('lastname')
    genre = request.GET.get('genre', 'all')
    release_date = request.GET.get('releaseDate', 9999)
    if firstname is None or lastname is None:
        raise ValueError('firstname and lastname need to be provided')

    return Key(firstname=firstname, lastname=lastname, genre=genre, release_date=release_date)


