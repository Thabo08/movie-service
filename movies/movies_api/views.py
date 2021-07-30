from django.http import HttpResponse
import requests
import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def actor_movies(request, firstname, lastname):
    resp = artist_movies(firstname, lastname)
    return HttpResponse(json.dumps(resp))


def artist_movies(firstname, lastname):
    response = requests.get(f'https://itunes.apple.com/search?term={firstname}+{lastname}&entity=movie')
    term = f'{firstname} {lastname}'
    all_movies = {term: []}
    if response.ok:
        movies = json.loads(response.content)['results']
        count = len(movies)
        print(f'Found {count} movies for artist: {firstname} {lastname}')
        for movie in movies:
            title = movie['trackName']
            all_movies.get(term).append(title)
    else:
        print(f'No movies found for artist: {firstname} {lastname}')
    return all_movies
