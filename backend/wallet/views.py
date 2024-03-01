from api.mixins import UserQuerySetMixin
from rest_framework import generics, permissions, status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Wallet
from .serializers import WalletSerializer


class WalletAPIView(UserQuerySetMixin, RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet = Wallet.objects.filter(user=self.request.user)
        print(wallet)
        return wallet.first()

    def get(self, request, *args, **kwargs):
        wallet = self.get_object()
        if not wallet:
            return Response({
                'message': 'You dont have wallet yet!',
                'create url': reverse(viewname='wallet-create', request=self.request)},
                status=status.HTTP_404_NOT_FOUND)
        return self.retrieve(request)

    # def get(self, request):
    #     wallet = self.get_queryset()
    #     if not wallet.exists():
    #         return Response(
    #             {'message': 'You dont have wallet yet!',
    #              'create url': reverse(viewname='wallet-create', request=self.request)}, status=status.HTTP_404_NOT_FOUND)
    #
    #     serializer = self.serializer_class(wallet.first())
    #     return Response(serializer.data)


class CreateWalletAPIView(generics.CreateAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
