""" This file contains the functionality to make requests and how to handle responses and errors """
import json

import requests
import pickle
from django.http import HttpResponse
from django.core.cache import caches
from .models import Key, Movies, Movie
from bson.binary import Binary
from bson.binary import USER_DEFINED_SUBTYPE

import logging
logger = logging.getLogger(__name__)


def get_storage(in_memory):
    if in_memory:
        logger.info("Using in memory storage")
        return InMemoryStorage()
    logger.info("Using in real storage")
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
        try:
            return self.storage.get(key)
        except Exception:
            raise

    def save_movies(self, key: Key, movies):
        logger.info(f"Saving movies for artist '{key.__str__()}' in the cache and the database")
        self.storage.put(key, movies)


class RequestResponse:
    """ This class does the actual api request and returns the response to the caller """
    def __init__(self):
        self.target_path = "https://itunes.apple.com/search?term={}+{}&entity=movie"

    def response(self, key: Key):
        return requests.get(self.target_path.format(key.get_firstname(), key.get_lastname()))


class ThirdParty:
    """ This class uses a third party API to lookup the requested information """

    def __init__(self, request_response: RequestResponse):
        self.request_response = request_response

    def api_lookup(self, key: Key) -> Movies:
        response = self.request_response.response(key)
        movies = Movies(artist_name=key)
        if response.ok:
            api_movies = json.loads(response.content)['results']
            count = len(api_movies)
            logger.debug(f"Found '{count}' movies for artist: {key}")
            for api_movie in api_movies:
                track_name = api_movie['trackName']
                release_date = api_movie['releaseDate']
                genre = api_movie['primaryGenreName']
                movies.add(Movie(track_name=track_name, release_date=release_date, primary_genre_name=genre))
        else:
            logger.error(f"Cannot get movies for {key}")
            raise ValueError(f"Cannot get movies for {key}")
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
        try:
            movies = self.storage.storage_lookup(key)
        except Exception:
            return HttpResponse("Internal server error", 500)

        if movies is None:
            try:
                logger.info(f"Looking up details for artist '{key}' from 3rd party api")
                movies = self.third_party.api_lookup(key)
                self.storage.save_movies(key, movies)
            except ValueError:
                return HttpResponse(f"Resource not found for {key}", 404)
        else:
            logger.info(f"Returning details for artist '{key}' from storage")
        return _filtered(movies, key)


request_response = RequestResponse()
third_party = ThirdParty(request_response)
cache_spi = CacheSpi(in_memory=False)


def get_response(key):
    try:
        handler = RequestHandler(cache_spi, third_party)
        return HttpResponse(handler.get_details(key).details())
    except AttributeError:
        return HttpResponse("Internal server error", 500)
