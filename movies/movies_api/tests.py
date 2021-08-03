import json
from django.test import TestCase
from unittest import mock

from .movie_requests import *
from .models import Key, Movies, Movie

kevin_key = Key('kevin', 'hart')
test_movies = [
    Movie('title_1', '2013-07-03T07:00:00Z', 'Comedy'),
    Movie('title_2', '2017-07-03T07:00:00Z', 'Drama'),
    Movie('title_3', '2020-07-03T07:00:00Z', 'Thriller')
]


class KeyTests(TestCase):

    def test_keys_with_same_firstname_lastname_are_equal(self):
        key_2 = Key('kevin', 'hart')
        self.assertEqual(kevin_key, key_2, "Keys with same firstname and lastname need to be equal")

    def test_keys_with_different_firstname_lastname_are_not_equal(self):
        key_2 = Key('brad', 'pitt')
        self.assertNotEqual(kevin_key, key_2, "Keys with different firstname and lastname need to be unequal")


class RequestHandlerTests(TestCase):

    def __init__(self, *args, **kwargs):
        super(RequestHandlerTests, self).__init__(*args, **kwargs)
        self.movies = Movies(artist_name=kevin_key)

        for test_movie in test_movies:
            self.movies.add(test_movie)

        self.mock_details = self.movies.details()

    @mock.patch('movies_api.movie_requests.CacheSpi')
    @mock.patch('movies_api.movie_requests.ThirdParty')
    def test_should_lookup_details_from_third_party_if_not_in_storage(self, cache, third_party):
        # given
        handler = RequestHandler(cache, third_party)
        cache.storage_lookup.return_value = None

        # when
        handler.get_details(kevin_key)

        # then
        third_party.api_lookup.assert_called_with(kevin_key)
        cache.save_movies.assert_called()  # todo: Test that this is called with the correct details

    @mock.patch('movies_api.movie_requests.CacheSpi')
    @mock.patch('movies_api.movie_requests.ThirdParty')
    def test_should_not_lookup_details_from_third_party_if_in_storage(self, cache, third_party):
        # given
        handler = RequestHandler(cache, third_party)
        cache.storage_lookup.return_value = self.mock_details

        # when
        handler.get_details(kevin_key)

        # then
        third_party.api_lookup.assert_not_called()

    def test_should_return_all_movies_if_no_filtering_applied(self):
        # given
        in_mem_cache = CacheSpi(in_memory=True)
        in_mem_cache.save_movies(kevin_key, self.mock_details)
        handler = RequestHandler(in_mem_cache, ThirdParty())

        # when
        details = handler.get_details(kevin_key)

        # then
        for t_movie, j_movie in zip(test_movies, json.loads(details)['kevin hart']):
            self.assertTrue(str(t_movie) == j_movie['name'])

    def test_should_return_only_movies_matching_genre(self):
        # given
        key_with_genre = Key(firstname=kevin_key.get_firstname(), lastname=kevin_key.get_lastname(),
                             genre='Drama')
        in_mem_cache = CacheSpi(in_memory=True)
        in_mem_cache.save_movies(key_with_genre, self.movies)
        handler = RequestHandler(in_mem_cache, ThirdParty())

        # when
        details = handler.get_details(key_with_genre)

        # then
        self.assertTrue(len(details.all_movies()) == 1)
        self.assertTrue(details.all_movies()[0]['genre'] == 'Drama')

    def test_should_return_only_movies_matching_release_date(self):
        # given
        key_with_release_date = Key(firstname=kevin_key.get_firstname(), lastname=kevin_key.get_lastname(),
                                    release_date=2020)
        in_mem_cache = CacheSpi(in_memory=True)
        in_mem_cache.save_movies(key_with_release_date, self.movies)
        handler = RequestHandler(in_mem_cache, ThirdParty())

        # when
        details = handler.get_details(key_with_release_date)

        # then
        self.assertTrue(len(details.all_movies()) == 1)
        self.assertTrue(details.all_movies()[0]['name'] == 'title_3')

    def test_should_return_only_movies_matching_genre_and_release_date(self):
        # given
        key_with_genre_and_release_date = Key(firstname=kevin_key.get_firstname(), lastname=kevin_key.get_lastname(),
                                              genre='Comedy', release_date=2013)
        in_mem_cache = CacheSpi(in_memory=True)
        in_mem_cache.save_movies(key_with_genre_and_release_date, self.movies)
        handler = RequestHandler(in_mem_cache, ThirdParty())

        # when
        details = handler.get_details(key_with_genre_and_release_date)

        self.assertTrue(len(details.all_movies()) == 1)
        self.assertTrue(details.all_movies()[0]['name'] == 'title_1')


class MoviesTests(TestCase):

    def test_should_add_movies(self):
        movies = Movies(artist_name=kevin_key)
        test_movies = [
            Movie('title_1', '2013-07-03T07:00:00Z', 'Comedy'),
            Movie('title_2', '2017-07-03T07:00:00Z', 'Drama'),
            Movie('title_3', '2020-07-03T07:00:00Z', 'Thriller')
        ]

        for test_movie in test_movies:
            movies.add(test_movie)

        self.assertTrue(len(movies.all_movies()) == 3)
