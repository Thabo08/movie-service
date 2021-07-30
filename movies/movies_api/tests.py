from django.test import TestCase


class SampleTest(TestCase):

    def test_something(self):
        self.assertIs(2 > 3, False)

    def test_something2(self):
        self.assertIs(2 < 3, True)
