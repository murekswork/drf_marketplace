from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from wallet.models import Wallet


class WalletModelTestCase(TestCase):

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username="user1", email="user1@mail"
        )
        self.user1.set_password("0xABAD1DEA")
        self.user2 = get_user_model().objects.create_user(
            username="user2", email="user2@mail"
        )
        self.user2.set_password("0xABAD1DEA")

        self.wallet1 = Wallet.objects.create(user=self.user1)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=1000)

    def test_wallet_str(self):
        self.assertEqual(self.wallet1.__str__(), "user1s wallet")
        self.assertEqual(self.wallet2.__str__(), "user2s wallet")

    def test_wallet_balance(self):
        self.assertEqual(self.wallet1.balance, 0)
        self.assertEqual(self.wallet2.balance, 1000)

    def test_create_second_wallet_with_same_user_then_raise_error(self):
        with self.assertRaises(IntegrityError):
            Wallet.objects.create(user=self.user1)

    def test_wallet_user(self):
        self.assertEqual(self.wallet1.user, self.user1)
        self.assertEqual(self.wallet2.user, self.user2)
