from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from shop.models import Shop, ShopManager, ShopStaffGroup


class ShopModelTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_shop_user", email="test_shop_user@email.com"
        )
        self.user.set_password(raw_password="0xABAD1DEA")
        self.user.save()
        self.client.force_login(self.user)

    def test_create_shop(self):
        shop = Shop.objects.create(
            user=self.user, title="test_shop", description="test_shop_description"
        )
        shop.save()
        self.assertEqual(shop.title, "test_shop")
        self.assertEqual(shop.description, "test_shop_description")
        self.assertEqual(shop.user, self.user)


class TestShopStaffGroupModelTestCase(TestCase):

    def setUp(self):
        self.shop_owner = get_user_model().objects.create(
            username="owner", email="owner@email.com"
        )
        self.shop = Shop.objects.create(
            title="Test Shop", description="Test Shop", user=self.shop_owner
        )
        self.shop_staff_group = ShopStaffGroup.objects.create(
            group_name="Product Owner"
        )

        self.shop_staff_group.permissions.set(
            Permission.objects.filter(content_type__app_label="shop")
        )

    def test_shop_staff_group_permissions(self):
        self.assertIn(
            Permission.objects.get(codename="create_shop_product"),
            self.shop_staff_group.permissions.select_related(),
        )
        self.assertNotIn(
            Permission.objects.get(codename="add_product"),
            self.shop_staff_group.permissions.select_related(),
        )

    def test_shop_staff_group_has_permissions_when_has_permission(self):
        self.assertTrue(self.shop_staff_group.has_permission("create_shop_product"))
        self.assertTrue(self.shop_staff_group.has_permission("delete_shop_product"))
        self.assertTrue(self.shop_staff_group.has_permission("update_shop_product"))

    def test_shop_staff_group_has_permissions_when_has_not_permission(self):
        self.assertFalse(self.shop_staff_group.has_permission("add_product"))


class TestShopManagerModelTestCase(TestCase):

    def setUp(self):
        self.shop_owner = get_user_model().objects.create(
            username="owner", email="owner@email.com"
        )
        self.shop = Shop.objects.create(
            title="Test Shop", description="Test Shop", user=self.shop_owner
        )

        self.product_manager_group = ShopStaffGroup.objects.create(
            group_name="Product Manager"
        )
        self.product_manager_group.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "create_shop_product",
                    "update_shop_product",
                    "delete_shop_product",
                ]
            )
        )
        self.user_manager = get_user_model().objects.create(
            username="product_manager", email="dummy@mail.com"
        )
        self.shop_manager = ShopManager(
            user=self.user_manager,
            title="Product Manager Full",
            group=self.product_manager_group,
            shop=self.shop,
        )
        self.shop_manager.save()

    def test_shop_manager_fields(self):
        self.assertEqual(self.shop_manager.user, self.user_manager)
        self.assertEqual(self.shop_manager.title, "Product Manager Full")
        self.assertEqual(self.shop_manager.group, self.product_manager_group)
        self.assertEqual(self.shop_manager.shop, self.shop)

    def test_shop_manager_in_shop_managers_set(self):
        self.assertIn(self.user_manager, self.shop.managers.select_related())

    def test_shop_manager_has_permissions_when_which_his_group_has(self):
        user_role = self.shop.managers.through.objects.filter(user=self.user_manager)
        self.assertTrue(user_role[0].has_permission("create_shop_product"))
        self.assertTrue(user_role[0].has_permission("update_shop_product"))
        self.assertTrue(user_role[0].has_permission("delete_shop_product"))

    def test_shop_manager_does_not_have_permission_which_his_group_does_not_have(self):
        user_role = self.shop.managers.through.objects.filter(user=self.user_manager)
        self.assertFalse(user_role[0].has_permission("create_shop_sales"))
        self.assertFalse(user_role[0].has_permission("delete_shop_sales"))
        self.assertFalse(user_role[0].has_permission("update_shop_sales"))

    def test_shop_owner_has_all_permissions(self):
        for permission in [
            "create_shop_product",
            "update_shop_product",
            "delete_shop_product",
            "create_shop_sales",
            "update_shop_sales",
            "delete_shop_sales",
            "manage_shop_data",
            "can_manage_shop_managers",
        ]:
            self.assertTrue(
                self.shop.managers.through.objects.filter(user=self.shop_owner)[
                    0
                ].has_permission(permission)
            )
