from django.contrib.auth import get_user_model
from django.test import TestCase

from shop.models import Shop


class ShopModelTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test_shop_user', email='test_shop_user@email.com')
        self.user.set_password(raw_password='0xABAD1DEA')
        self.user.save()
        self.client.force_login(self.user)

    def test_create_shop(self):
        shop = Shop.objects.create(user=self.user, title='test_shop', description='test_shop_desciption')
        shop.save()
        self.assertEquals(shop.title, 'test_shop')
        self.assertEquals(shop.description, 'test_shop_description')
        self.assertEquals(shop.user, self.user)