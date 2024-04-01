import uuid

from django.contrib.auth import get_user_model
from django.db import models


class WalletQuerySet(models.QuerySet):

    pass


class WalletManager(models.Manager):

    def get_queryset(self):
        return WalletQuerySet(self.model, using=self._db)


class Wallet(models.Model):

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.OneToOneField(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True
    )
    balance = models.DecimalField(max_digits=50, decimal_places=4, default=0)

    def __str__(self):
        return f'{self.user}s wallet'


# Create your models here.
