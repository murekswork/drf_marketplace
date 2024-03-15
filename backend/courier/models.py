from django.db import models


class Courier(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=120, default='username')
    first_name = models.CharField(max_length=120, default='Couriers name')
    last_name = models.CharField(max_length=120, default='Couriers last name')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    done_deliveries = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    rank = models.FloatField(max_length=5, default=5)

    def __str__(self):
        return f'Courier {self.id} - {self.first_name} {self.last_name}'
