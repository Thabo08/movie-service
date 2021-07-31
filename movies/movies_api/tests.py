from django.test import TestCase
from unittest import mock

from .movie_requests import *
from .models import Key


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
        key_1 = Key('kevin', 'hart')
        key_2 = Key('kevin', 'hart')
        self.assertEqual(key_1, key_2, "Keys with same firstname and lastname need to be equal")

    def test_keys_with_different_firstname_lastname_are_not_equal(self):
        key_1 = Key('kevin', 'hart')
        key_2 = Key('brad', 'pitt')
        self.assertNotEqual(key_1, key_2, "Keys with different firstname and lastname need to be unequal")


class RequestHandlerTests(TestCase):

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
        key = Key('kevin', 'hart')
        handler = RequestHandler.get_instance(storage, third_party)
        storage.storage_lookup.return_value = None
        # third_party.api_lookup(key).return_value = HttpResponse('third party api response')

        # when
        handler.get_details(key)

        # then
        third_party.api_lookup.assert_called_with(key)

    @mock.patch('movies_api.movie_requests.StorageSpi')
    @mock.patch('movies_api.movie_requests.ThirdParty')
    def test_should_not_lookup_details_from_third_party_if_in_storage(self, storage, third_party):
        # given
        key = Key('kevin', 'hart')
        handler = RequestHandler.get_instance(storage, third_party)
        storage.storage_lookup.return_value = HttpResponse('storage response')

        # when
        handler.get_details(key)

        # then
        third_party.api_lookup.assert_not_called()
