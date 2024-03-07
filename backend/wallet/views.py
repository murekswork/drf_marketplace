from rest_framework.generics import get_object_or_404

from api.mixins import UserQuerySetMixin
from rest_framework import generics, permissions, status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Wallet
from .serializers import WalletSerializer


class WalletAPIView(UserQuerySetMixin, generics.GenericAPIView):
    serializer_class = WalletSerializer
    # queryset = Wallet.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]

    # def get_object(self):
    #     wallet = get_object_or_404(Wallet, user=self.request.user)
    #     self.kwargs['wallet']  = wallet
    #     return wallet

    def get(self, request, *args, **kwargs):
        wallet = get_object_or_404(Wallet, user=self.request.user)

        if not wallet:
            return Response({
                'message': 'You dont have wallet yet!',
                'create url': reverse(viewname='wallet-create', request=self.request)},
                status=status.HTTP_404_NOT_FOUND)

        return Response(self.serializer_class(wallet).data, status=status.HTTP_200_OK)

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
