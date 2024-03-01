from django.test import TestCase
from django.contrib.auth import get_user_model
from wallet.models import Wallet
from wallet.serializers import WalletSerializer


class TestWalletSerializer(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='serializertest', email='serializertest@email.com')
        self.user.set_password('afjosoaj21424')
        self.wallet = Wallet.objects.create(user=self.user)

    def test_wallet_serializer(self):
        wallet = Wallet.objects.get(user=self.user)
        serializer = WalletSerializer(wallet)
        self.assertEquals(serializer.data['id'], str(self.wallet.id))
        self.assertEquals(serializer.data['user'], self.user.id)
        self.assertEquals(serializer.data['balance'], '0.00')