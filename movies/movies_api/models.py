import json

from django.db import models
import datetime

def equality_tester(self_, clazz, other):
    if isinstance(other, clazz):
        for var in vars(self_):
            var_of_self = getattr(self_, var)
            var_of_other = getattr(other, var)

            if var_of_self != var_of_other:
                return False
        return True
    return False


class Key:
    """ Encapsulates a search query used for lookups """

    def __init__(self, firstname: str, lastname: str, genre='all', release_date=9999):
        """
        :param firstname: First name of an artist, eg, 'kevin' in 'Kevin Hart'
        :param lastname: Last name of an artist, eg, 'hart' in 'Kevin Hart'
        """
        self.firstname = firstname
        self.lastname = lastname
        self.genre = genre
        self.release_date = release_date
        self.key = f'{firstname}_{lastname}'
        self.filter = genre != 'all' or release_date != 9999

    def __eq__(self, other):
        return equality_tester(self, Key, other)

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return self.key.replace("_", " ")

    def get_firstname(self):
        return self.firstname

    def get_lastname(self):
        return self.lastname

    def get_genre(self):
        return self.genre

    def get_release_date(self):
        return int(self.release_date)

    def as_key(self):
        return self.key

    def apply_filter(self):
        return self.filter

    def filter_by_genre_only(self):
        return self.filter and self.genre != 'all' and self.release_date == 9999

    def filter_by_release_date_only(self):
        return self.filter and self.genre == 'all' and self.release_date != 9999


class Movie:
    """ This holds details about a movie for an artist """

    def __init__(self, track_name, release_date, primary_genre_name):
        """"
            :param track_name: The name of the movie
            :param release_date: The date when the movie was released
            :param primary_genre_name: The genre of the movie
        """
        self.track_name = track_name
        self.release_date = extract_release_date(release_date)
        self.primary_genre_name = primary_genre_name

    def details(self):
        return {
            "name": self.track_name,
            "release date": self.release_date,
            "genre": self.primary_genre_name
        }

    def __str__(self):
        return self.track_name


class Movies:
    """ This holds all the movies for an artist """

    def __init__(self, artist_name: Key):
        """
        :param artist_name: The name of the artist, held in a Key object
        """
        self.key = artist_name.__str__()
        self.movies = {self.key: []}  # container that holds all the movies

    def add(self, movie: Movie):
        print(f"Info: Adding movie '{movie.__str__()}' for artist '{self.key.__str__()}'")
        self.movies.get(self.key).append(movie.details())

    def all_movies(self):
        return self.movies.get(self.key)

    def details(self):
        return json.dumps(self.movies)


def extract_release_date(as_string):
    try:
        year, _, _ = as_string.split('T')[0].split('-')
        return int(year)
    except (AttributeError, ValueError):
        # todo: do this better
        return int(as_string)