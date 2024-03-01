from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
import requests

from wallet.models import Wallet


class WalletAPIViewTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testview', email='testview@email.com')
        self.user.set_password('0xABAD1DEA')
        self.user.save()
        response = self.client.post(reverse('token-auth'),
                                 data={'username': 'testview', 'password': '0xABAD1DEA'})

        self.token = response.json()['token']

    def test_wallet_api_view_anonymous_user_then_return_403(self):
        response = self.client.get(reverse('wallet'))
        self.assertEquals(response.status_code, 403)

    def test_wallet_api_view_logged_in_user_no_wallet(self):
        self.client.force_login(self.user)
        print(self.client)
        response = self.client.get(reverse('wallet'), headers={'Authorization': f'Bearer {self.token}'})
        self.assertEquals(response.status_code, 404)

    def test_wallet_api_view_when_user_has_wallet(self):
        wallet = Wallet.objects.create(user=self.user)
        response = self.client.get(reverse('wallet'), headers={'Authorization': f'Bearer {self.token}'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['balance'], '0.00')

    def test_create_wallet_api_view_when_anonymous_user_then_raise_error(self):
        response = self.client.post(reverse('wallet-create'))
        self.assertEquals(response.status_code, 403)

    def test_create_wallet_api_view_when_user_has_not_wallet_then_create_wallet(self):
        response = self.client.post(reverse('wallet-create'), headers={'Authorization': f'Bearer {self.token}'})
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.json()['balance'], '0.00')

    def test_create_wallet_api_view_when_use_has_wallet_then_raise_error(self):
        wallet = Wallet.objects.create(user=self.user)
        response = self.client.post(reverse('wallet-create'), headers={'Authorization': f'Bearer {self.token}'})
        self.assertEquals(response.status_code, 400)

