# Generated by Django 5.0.2 on 2024-03-15 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                (
                    'id',
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                (
                    'first_name',
                    models.CharField(default='Couriers name', max_length=120),
                ),
                (
                    'last_name',
                    models.CharField(default='Couriers last name', max_length=120),
                ),
                (
                    'balance',
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ('complete_orders', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'rank',
                    models.DecimalField(decimal_places=2, default=5, max_digits=3),
                ),
            ],
        ),
    ]
