# Generated by Django 5.0.2 on 2024-03-13 21:31

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0007_alter_order_lifetime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 3, 13, 21, 31, 27, 31630)
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="lifetime",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 3, 13, 21, 33, 27, 31689)
            ),
        ),
    ]