""" This file contains the functionality to make requests and how to handle responses and errors """

import requests
from django.http import HttpResponse
from requests import Response
from .models import Key


class StorageSpi:
    """ This is an interface for the storage"""

    def storage_lookup(self, key: Key):
        return None


class ThirdParty:
    """ This class uses a third party API to lookup the requested information """

    def __init__(self):
        pass

    def api_lookup(self, key: Key):
        return None


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


class RequestHandler:
    """ This singleton class handles requests and responses. It is the entry and exit point of the api """
    __instance = None

    @staticmethod
    def get_instance(storage: StorageSpi, third_party: ThirdParty):
        if RequestHandler.__instance is None:
            print("debug: Creating new request handler")
            RequestHandler(storage, third_party)
        return RequestHandler.__instance

    def __init__(self, storage, third_party):
        self.storage = storage
        self.third_party = third_party

        if RequestHandler.__instance is not None:
            raise Exception("Instance of this class cannot be created again! Singleton violation!")
        else:
            RequestHandler.__instance = self

    def get_details(self, key) -> HttpResponse:
        """ This returns the details being looked up for based on the provided key
            :param key: The lookup key
        """
        details = self.storage.storage_lookup(key)
        if details is None:
            print(f"info: Looking up details for artist '{key.__str__()}' from 3rd party api")
            return self.third_party.api_lookup(key)
        # self.third_party.api_lookup(key)
        return details
