import random
from django.db import models

class Courier(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=120, blank=True, null=True)
    first_name = models.CharField(max_length=120, default='Couriers name')
    last_name = models.CharField(max_length=120, default='Couriers last name')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    done_deliveries = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    rank = models.FloatField(max_length=5, default=5)

    def __str__(self):
        return f"Courier {self.id} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{self.first_name}_{self.last_name}_{random.randint(1, 1000)}"
        super().save(*args, **kwargs)
