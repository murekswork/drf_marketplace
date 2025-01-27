# Generated by Django 5.0.2 on 2024-03-08 14:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductUpload',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('products_count', models.IntegerField(default=0)),
                ('success_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('file_name', models.CharField(blank=True, max_length=250, null=True)),
                (
                    'user',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('title', models.CharField(default='Shop Title', max_length=120)),
                (
                    'description',
                    models.TextField(default='Shop Description', max_length=500),
                ),
                ('active', models.BooleanField(default=True)),
                ('slug', models.SlugField(editable=False, max_length=500, unique=True)),
                (
                    'user',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='shop_owned',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ShopManager',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('title', models.CharField(max_length=120, null='Role title')),
                (
                    'shop',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='shop.shop',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='shop',
            name='managers',
            field=models.ManyToManyField(
                through='shop.ShopManager', to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name='ShopStaffGroup',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('group_name', models.CharField(default='Group name', max_length=120)),
                (
                    'permissions',
                    models.ManyToManyField(
                        blank=True,
                        limit_choices_to={
                            'codename__in': [
                                'add_product',
                                'delete_product',
                                'delete_sale',
                                'change_product',
                                'change_sale',
                                'add_sale',
                            ]
                        },
                        to='auth.permission',
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='shopmanager',
            name='group',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='shop.shopstaffgroup',
            ),
        ),
    ]
