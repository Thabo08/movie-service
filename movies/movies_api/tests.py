from django.test import TestCase
from unittest import mock

from .movie_requests import *
from .models import Key, Movies, Movie

kevin_key = Key('kevin', 'hart')


class RequestsTests(TestCase):

    @mock.patch('movies_api.movie_requests.StorageSpi')
    @mock.patch('movies_api.movie_requests.ResponseBuilder')
    def test_should_return_client_error_for_invalid_requests(self, storage, response):
        response.request_response("test").status_code.return_value = 403
        storage.contains.return_value = False

        data = get_data(storage, response)
        self.assertContains(data, 'Error handler content', status_code=403)


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
        self.mock_details = Movies(artist_name=kevin_key).details()

    @mock.patch('movies_api.movie_requests.StorageSpi')
    @mock.patch('movies_api.movie_requests.ThirdParty')
    def test_should_not_create_another_instance_if_already_exist(self, storage, third_party):
        handler1 = RequestHandler.get_instance(storage, third_party)
        handler2 = RequestHandler.get_instance(storage, third_party)

        self.assertEqual(handler1, handler2, "Singleton class object should not be recreated")

    @mock.patch('movies_api.movie_requests.StorageSpi')
    @mock.patch('movies_api.movie_requests.ThirdParty')
    def test_should_lookup_details_from_third_party_if_not_in_storage(self, storage, third_party):
        # given
        handler = RequestHandler.get_instance(storage, third_party)
        storage.storage_lookup.return_value = None

        # when
        handler.get_details(kevin_key)

        # then
        third_party.api_lookup.assert_called_with(kevin_key)
        storage.save_details.assert_called()  # todo: Test that this is called with the correct details

    @mock.patch('movies_api.movie_requests.StorageSpi')
    @mock.patch('movies_api.movie_requests.ThirdParty')
    def test_should_not_lookup_details_from_third_party_if_in_storage(self, storage, third_party):
        # given
        handler = RequestHandler.get_instance(storage, third_party)
        storage.storage_lookup.return_value = self.mock_details

        # when
        handler.get_details(kevin_key)

        # then
        third_party.api_lookup.assert_not_called()


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

        # todo: Test this properly
        details = movies.details()
        print(details)
