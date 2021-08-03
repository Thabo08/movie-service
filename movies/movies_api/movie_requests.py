""" This file contains the functionality to make requests and how to handle responses and errors """
import json

import requests
import pickle
from django.http import HttpResponse
from django.core.cache import caches
from .models import Key, Movies, Movie
from bson.binary import Binary
from bson.binary import USER_DEFINED_SUBTYPE


def get_storage(in_memory):
    if in_memory:
        print("info: Using in memory storage")
        return InMemoryStorage()
    print("info: Using in real storage")
    return MemCached()


def to_binary(movies: Movies):
    return Binary(pickle.dumps(movies), USER_DEFINED_SUBTYPE)


class MemCached:
    def __init__(self):
        self.memcached = caches['default']

    def put(self, key, details):
        self.memcached.add(key.as_key(), details)

    def get(self, key):
        return self.memcached.get(key.as_key())


class InMemoryStorage:
    """ This uses a python dictionary for storage. Mainly used for testing without starting up memcached """
    def __init__(self):
        self.storage = {}

    def put(self, key, details):
        self.storage[key] = details

    def get(self, key):
        return self.storage.get(key)


class CacheSpi:
    """ This is a service provider interface for the storage"""
    def __init__(self, in_memory=False):
        self.storage = get_storage(in_memory)

    def storage_lookup(self, key: Key):
        return self.storage.get(key)

    def save_movies(self, key: Key, movies):
        print(f"info: Saving movies for artist '{key.__str__()}' in the cache and the database")
        self.storage.put(key, movies)


class ThirdParty:
    """ This class uses a third party API to lookup the requested information """

    def __init__(self):
        pass

    def api_lookup(self, key: Key) -> Movies:
        movies = Movies(artist_name=key)
        firstname = key.get_firstname()
        lastname = key.get_lastname()
        # todo : Abstract this out to improve testability
        response = requests.get(f'https://itunes.apple.com/search?term={firstname}+{lastname}&entity=movie')
        if response.ok:
            api_movies = json.loads(response.content)['results']
            count = len(api_movies)
            print(f"Found '{count}' movies for artist: {key.__str__()}")
            for api_movie in api_movies:
                track_name = api_movie['trackName']
                release_date = api_movie['releaseDate']
                genre = api_movie['primaryGenreName']
                movies.add(Movie(track_name=track_name, release_date=release_date, primary_genre_name=genre))
        return movies


def _filtered(movies, key):
    if not key.apply_filter():
        return movies
    else:
        filtered_movies = Movies(key)
        if key.filter_by_genre_only():
            for movie in movies.all_movies():
                track_name, release_date, genre = _details(movie)
                if genre.lower() == key.get_genre().lower():
                    filtered_movies.add(Movie(track_name, release_date, genre))
        elif key.filter_by_release_date_only():
            for movie in movies.all_movies():
                track_name, release_date, genre = _details(movie)
                if release_date == key.get_release_date():
                    filtered_movies.add(Movie(track_name, release_date, genre))
        else:
            # filter by both genre and release date
            for movie in movies.all_movies():
                track_name, release_date, genre = _details(movie)
                if genre.lower() == key.get_genre().lower() and release_date == key.get_release_date():
                    filtered_movies.add(Movie(track_name, release_date, genre))
        return filtered_movies


def _details(movie):
    return movie['name'], movie['release date'], movie['genre']


class RequestHandler:
    """ This class handles requests and responses. It is the entry and exit point of the api """

    def __init__(self, storage, third_party):
        self.storage = storage
        self.third_party = third_party

    def get_details(self, key):
        """ This returns the details being looked up for based on the provided key
            :param key: The lookup key
        """
        movies = self.storage.storage_lookup(key)
        if movies is None:
            print(f"info: Looking up details for artist '{key.__str__()}' from 3rd party api")
            movies = self.third_party.api_lookup(key)
            self.storage.save_movies(key, movies)
        else:
            print(f"info: Returning details for artist '{key.__str__()}' from storage")
        return _filtered(movies, key)


# todo: Delete this - only for testing purposes
def test_helper(key):
    handler = RequestHandler(CacheSpi(in_memory=False), ThirdParty())
    return HttpResponse(handler.get_details(key).details())