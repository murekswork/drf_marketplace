# Generated by Django 5.0.2 on 2024-03-15 22:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("courier", "0004_alter_courier_rank"),
        ("order", "0009_alter_order_created_at_alter_order_lifetime"),
    ]

    operations = [
        migrations.CreateModel(
            name="Delivery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.CharField(max_length=120)),
                ("latitude", models.FloatField(max_length=15)),
                ("longitude", models.FloatField(max_length=15)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("searching", "Searching"),
                            ("in-process", "In Process"),
                            ("delivered", "Delivered"),
                            ("canceled", "Canceled"),
                        ],
                        max_length=10,
                    ),
                ),
                ("amount", models.FloatField(max_length=6)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "courier",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="courier.courier",
                    ),
                ),
                (
                    "order_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery",
                        to="order.order",
                    ),
                ),
            ],
        ),
    ]
