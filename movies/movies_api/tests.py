from django.test import TestCase
from unittest import mock

from .movie_requests import *


class RequestsTests(TestCase):

    @mock.patch('movies_api.movie_requests.StorageSpi')
    @mock.patch('movies_api.movie_requests.ResponseBuilder')
    def test_should_return_client_error_for_invalid_requests(self, storage, response):
        response.request_response("test").status_code.return_value = 403
        storage.contains.return_value = False

        data = get_data(storage, response)
        self.assertContains(data, 'Error handler content', status_code=403)


class SampleTest(TestCase):

    def test_something(self):
        self.assertIs(2 > 3, False)

    def test_something2(self):
        self.assertIs(2 < 3, True)
