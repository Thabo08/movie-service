""" This file contains the functionality to make requests and how to handle responses and errors """

import requests
from django.http import HttpResponse
from requests import Response


class StorageSpi:
    """ This is an interface for the storage"""

    def contains(self, key):
        pass


class ResponseBuilder:

    def request_response(self, url) -> Response:
        return requests.get(url)


def get_data(storage: StorageSpi, response: ResponseBuilder) -> HttpResponse:
    if storage.contains(""):
        return HttpResponse()
    else:
        #        response.request_response("test").status_code.return_value = 403
        status = response.request_response("test").status_code
        return HttpResponse('Error handler content', status=403)
