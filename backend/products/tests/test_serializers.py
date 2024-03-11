from django.contrib.auth import get_user_model
from django.test import TestCase


class ProductSerializerTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', email='test@email.com')
