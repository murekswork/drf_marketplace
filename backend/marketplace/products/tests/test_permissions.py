from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from products.models import Product
from shop.models import Shop, ShopManager, ShopStaffGroup

User = get_user_model()


class TestManagerPermissions(TestCase):

    def setUp(self):
        self.user_owner = User.objects.create_user(
            username="user_owner", email="user_owner@mail.com"
        )
        self.shop = Shop.objects.create(
            user=self.user_owner, title="test_shop", description="test_shop"
        )

        self.product_manager_group = ShopStaffGroup.objects.create(
            group_name="Product Managers",
        )
        self.product_manager = User.objects.create_user(
            username="product_manager", email="product_naager@email.com"
        )
        for perm in [
            Permission.objects.filter(
                codename__in=[
                    "create_shop_product",
                    "update_shop_product",
                    "delete_shop_product",
                ]
            ).all()
        ]:
            self.product_manager_group.permissions.add(perm)
        self.product_manager_group.save()
        self.product_manager_role = ShopManager.objects.create(
            shop=self.shop, group=self.product_manager_group, user=self.product_manager
        )
        self.product_manager_role.save()

        self.sales_manager_group = ShopStaffGroup.objects.create(
            group_name="Sales Managers"
        )
        for perm in [
            Permission.objects.filter(
                codename__in=[
                    "create_shop_sales",
                    "update_shop_sales",
                    "delete_shop_sales",
                ]
            ).all()
        ]:
            self.sales_manager_group.permissions.add(perm)
        self.sales_manager_group.save()
        self.sales_manager = User.objects.create_user(
            username="sales_manager", email="salesmanager@email.com"
        )
        self.sales_manager_role = ShopManager.objects.create(
            shop=self.shop, group=self.sales_manager_group, user=self.sales_manager
        )

        self.sales_manager_role.save()

        self.product = Product.objects.create(
            public=True, title="prodict", content="Content", price=15, shop=self.shop
        )


def test_user_owner_access_permission_can_upload_product(self):
    self.client.force_login(self.user_owner)
    response = self.client.post(
        reverse("product-list"),
        data={
            "title": "title",
            "content": "content",
            "price": 12000,
            "quantity": 1,
            "shop": self.shop.id,
        },
        follow=True,
    )
    self.assertTrue(response.status_code == 201)


def test_user_owner_access_permission_can_update_product(self):
    self.client.force_login(self.user_owner)
    response = self.client.put(
        reverse("product-update", kwargs={"pk": self.product.pk}),
        data={"title": "new title", "content": "new content", "price": 25000},
        content_type="application/json",
        follow=True,
    )
    self.assertTrue(response.status_code == 200)


def test_user_owner_access_permission_can_create_sale(self): ...


def test_user_owner_access_permission_can_update_sale(self): ...


def test_user_product_manager_access_permission_can_upload_product(self):
    self.client.force_login(self.product_manager)
    response = self.client.post(
        reverse("product-list"),
        data={
            "title": "title2",
            "content": "content2",
            "price": 12000,
            "quantity": 1,
            "shop": self.shop.id,
        },
        follow=True,
    )
    self.assertTrue(response.status_code == 201)


def test_user_product_manager_access_permission_can_update_product(self):
    self.client.force_login(self.product_manager)
    response = self.client.put(
        reverse("product-update", kwargs={"pk": self.product.pk}),
        data={"title": "new title", "content": "new content", "price": 25},
        content_type="application/json",
    )
    self.assertEqual(response.status_code, 200, "updated product by product manager")


def test_user_sales_manager_access_permission_can_not_upload_product(self):
    self.client.force_login(self.sales_manager)
    response = self.client.post(
        reverse("product-list"),
        data={
            "title": "title3",
            "content": "content3",
            "price": 12000,
            "quantity": 1,
            "shop": self.shop.id,
        },
        follow=True,
    )
    self.assertTrue(response.status_code == 403)


def test_user_sales_manager_access_can_not_delete_product(self):
    self.client.force_login(self.sales_manager)
    response = self.client.delete(
        reverse("product-delete", kwargs={"pk": self.product.pk})
    )
    self.assertTrue(response.status_code != 204)


def test_user_sales_manager_access_permission_can_not_update_product(self):
    self.client.force_login(self.sales_manager)
    response = self.client.put(
        reverse("product-update", kwargs={"pk": self.product.pk}),
        data={"title": "new title", "content": "new content", "price": 25},
        content_type="application/json",
        follow=True,
    )
    self.assertTrue(response.status_code != 200)


def test_user_product_manager_access_permission_can_delete_product(self):
    self.client.force_login(self.product_manager)
    response = self.client.delete(
        reverse("product-delete", kwargs={"pk": self.product.pk})
    )
    self.assertEqual(response.status_code, 204, "product manager deletes product")


def test_user_owner_access_permission_can_delete_product(self):
    new_pr = Product.objects.create(
        shop=self.shop, title="new title", content="new content", price=25555
    )
    self.client.force_login(self.user_owner)
    response = self.client.delete(reverse("product-delete", kwargs={"pk": new_pr.pk}))
    self.assertTrue(response.status_code == 204)
