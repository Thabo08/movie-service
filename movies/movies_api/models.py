from django.db import models


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
    """ Encapsulates a key used for lookups """
    def __init__(self, firstname: str, lastname: str):
        """
        :param firstname: First name of an artist, eg, 'kevin' in 'Kevin Hart'
        :param lastname: Last name of an artist, eg, 'hart' in 'Kevin Hart'
        """
        self.firstname = firstname
        self.lastname = lastname
        self.key = f'{firstname} {lastname}'

    def __eq__(self, other):
        return equality_tester(self, Key, other)

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return self.key

    def get_firstname(self):
        return self.firstname

    def get_lastname(self):
        return self.lastname