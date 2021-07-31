from django.http import HttpResponse
import requests
import json

from .models import Key
from .movie_requests import test_helper


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def actor_movies(request, firstname, lastname):
    key = Key(firstname, lastname)
    return test_helper(key)
