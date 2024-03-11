from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from products.models import Product
from shop.models import Shop


class ProductListCreateAPIViewTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='user', email='usermail@mail.com')
        self.client.force_login(self.user)
        self.shop = Shop.objects.create(user=self.user, title='shop', description='shop')
        self.maxDiff = None

        with connection.cursor() as cursor:
            cursor.execute("SELECT setval('products_product_id_seq', 1, false)")
            cursor.execute("SELECT setval('shop_shop_id_seq', 1, false)")

    def test_product_list_when_logged_in_then_200(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_when_not_logged_in_then_200(self):
        self.client.logout()
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_when_no_products(self):
        response = self.client.get(reverse('product-list')).json()
        self.assertEqual(response, {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_product_list_when_some_products_when_loged_in(self):
        Product.objects.create(shop=self.shop, title='pr1', content='pr1', public=True)
        Product.objects.create(shop=self.shop, title='pr2', content='pr2', public=True)
        response = self.client.get(reverse('product-list')).json()
        expecting = {'count': 2,
                     'next': None,
                     'previous': None,
                     'results': [{'content': 'pr1',
                                  'mark': '5.00',
                                  'price': '99.99',
                                  'quantity': 0,
                                  'sale': None,
                                  'sale_price': None,
                                  'sales_count': 0,
                                  'seller': 'http://testserver/api/shop/shop/',
                                  'title': 'pr1',
                                  'url': 'http://testserver/api/products/1'},
                                 {'content': 'pr2',
                                  'mark': '5.00',
                                  'price': '99.99',
                                  'quantity': 0,
                                  'sale': None,
                                  'sale_price': None,
                                  'sales_count': 0,
                                  'seller': 'http://testserver/api/shop/shop/',
                                  'title': 'pr2',
                                  'url': 'http://testserver/api/products/2'}]}

        self.assertEqual(response, expecting)

    def test_product_list_when_some_products_when_not_loged_in(self):
        Product.objects.create(shop=self.shop, title='pr1', content='pr1', public=True)
        Product.objects.create(shop=self.shop, title='pr2', content='pr2', public=True)
        self.client.logout()
        response = self.client.get(reverse('product-list')).json()
        expecting = {'count': 2,
                     'next': None,
                     'previous': None,
                     'results': [{'content': 'pr1',
                                  'mark': '5.00',
                                  'price': '99.99',
                                  'quantity': 0,
                                  'sale': None,
                                  'sale_price': None,
                                  'sales_count': 0,
                                  'seller': 'http://testserver/api/shop/shop/',
                                  'title': 'pr1',
                                  'url': 'http://testserver/api/products/1'},
                                 {'content': 'pr2',
                                  'mark': '5.00',
                                  'price': '99.99',
                                  'quantity': 0,
                                  'sale': None,
                                  'sale_price': None,
                                  'sales_count': 0,
                                  'seller': 'http://testserver/api/shop/shop/',
                                  'title': 'pr2',
                                  'url': 'http://testserver/api/products/2'}]}

        self.assertEqual(response, expecting)

    def test_product_list_search_when_no_product(self):
        response = self.client.get(reverse('product-list'), search='product')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_product_list_search_when_found_in_product_title(self):
        Product.objects.create(shop=self.shop, title='product X', public=True)
        response = self.client.get(reverse('product-list'), search='product X')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 1,
                                           'next': None,
                                           'previous': None,
                                           'results': [{'content': None,
                                                        'mark': '5.00',
                                                        'price': '99.99',
                                                        'quantity': 0,
                                                        'sale': None,
                                                        'sale_price': None,
                                                        'sales_count': 0,
                                                        'seller': 'http://testserver/api/shop/shop/',
                                                        'title': 'product X',
                                                        'url': 'http://testserver/api/products/1'}]})

    def test_product_list_search_when_found_in_product_content(self):
        Product.objects.create(shop=self.shop, title='title', content='product X', public=True)
        response = self.client.get(reverse('product-list'), search='product X')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 1,
                                           'next': None,
                                           'previous': None,
                                           'results': [{'content': 'product X',
                                                        'mark': '5.00',
                                                        'price': '99.99',
                                                        'quantity': 0,
                                                        'sale': None,
                                                        'sale_price': None,
                                                        'sales_count': 0,
                                                        'seller': 'http://testserver/api/shop/shop/',
                                                        'title': 'title',
                                                        'url': 'http://testserver/api/products/1'}]}
                         )

    def test_product_list_search_when_products_are_not_public(self):
        Product.objects.create(shop=self.shop, title='product X')
        response = self.client.get(reverse('product-list'), search='product X')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_product_list_post_when_not_authenticated(self):
        self.client.logout()
        response = self.client.post(reverse('product-list'), data={'title': 'title', 'content': 'product'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_product_list_post_when_authenticated_and_no_data_provided(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('product-list'), data={})
        self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.json(), {'title': ['This field is required.'],
        #                                    'shop': ['This field is required.']})

    def test_product_list_post_when_authenticated_and_no_shop_provided_then_400(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('product-list'), data={'title': 'sometitle'})
        self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.json(),
        #                  {'shop': ['This field is required.']})

    def test_product_list_post_when_authenticated_and_no_title_provided_then_400(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('product-list'), data={'shop': 1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                         {'title': ['This field is required.']})

    def test_product_list_post_when_authenticated_and_invalid_shop_pk_provided_then_400(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('product-list'), data={'shop': 155, 'title': 'sometitle'})
        self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.json(),
        #                  {'shop': ['Invalid pk "155" - object does not exist.']})

    def test_product_list_post_when_authenticated_valid_shop_but_not_owned_by_request_user_then_400(self):
        not_shop_owner = get_user_model().objects.create_user(username='shop_owner', email='shop_owner_email@email.com')
        self.client.force_login(not_shop_owner)
        response = self.client.post(reverse('product-list'), data={'shop': self.shop.id, 'title': 'sometitle'})
        self.assertEqual(response.json(), ['You dont have permission to upload products in this shop'])
        self.assertEqual(response.status_code, 403)

    def test_product_list_post_when_authenticated_valid_shop_when_owned_by_request_user_then_201(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('product-list'), data={'shop': self.shop.id, 'title': 'sometitle'})
        self.assertEqual(response.json(), 'Your product will be published after short check up!')
        self.assertEqual(response.status_code, 201)

    def test_product_list_post_when_authenticated_valid_shop_when_valid_product_data_then_product_appears_in_shop(self):
        self.client.force_login(self.user)
        Product.objects.create(shop=self.shop, title='product', content='products_desc', public=True)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 1,
                                           'next': None,
                                           'previous': None,
                                           'results': [{'content': 'products_desc',
                                                        'mark': '5.00',
                                                        'price': '99.99',
                                                        'quantity': 0,
                                                        'sale': None,
                                                        'sale_price': None,
                                                        'sales_count': 0,
                                                        'seller': 'http://testserver/api/shop/shop/',
                                                        'title': 'product',
                                                        'url': 'http://testserver/api/products/1'}]})

    def test_product_list_post_when_authenticated_valid_shop_when_not_valid_product_data_then_product_appears_in_shop(
            self):
        self.client.force_login(self.user)
        Product.objects.create(shop=self.shop, title='хуй', content='products_desc', public=True)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json(), {'count': 1, 'next': None, 'previous': None, 'results': [
            {'title': 'product', 'content': 'products_desc', 'price': '99.99',
             'seller': 'http://testserver/api/shop/shop/', 'sale': None, 'sales_count': 0, 'sale_price': None,
             'url': 'http://testserver/api/products/1', 'mark': '5.00'}]})

        # self.assertEquals(response.status_code, 403)
        # self.assertEquals(response.json(), {'detail': 'Authentication credentials were not provided.'})


class ProductDetailAPIViewTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='user', email='usermail@mail.com')
        self.client.force_login(self.user)
        self.shop = Shop.objects.create(user=self.user, title='shop', description='shop')
        self.maxDiff = None

        with connection.cursor() as cursor:
            cursor.execute("SELECT setval('products_product_id_seq', 1, false)")
            cursor.execute("SELECT setval('shop_shop_id_seq', 1, false)")

    def test_product_detail_when_product_exists_then_200(self):
        # def mocked_create(self, validated_data):
        #     user = self.context.get('request').user
        #     if not user:
        #         raise serializers.ValidationError('User is not authenticated')
        #     obj = super().create(validated_data)
        #     obj.public = True
        #     obj.save()
        #     return obj
        #
        # mock_custom_method.side_effect = mocked_create
        product = Product.objects.create(shop=self.shop, title='title', content='content', public=True)
        response = self.client.get(reverse('product-detail', kwargs={'pk': product.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                         {'title': 'title', 'content': 'content', 'price': '99.99', 'sale': None, 'sales_count': 0,
                          'sale_price': None, 'url': 'http://testserver/api/products/1', 'reviews': [], 'category': [],
                          'edit_url': 'http://testserver/api/products/1/update', 'mark': '5.00',
                          'seller': 'http://testserver/api/shop/shop/'})

    def test_product_detail_when_product_does_not_exist_then_404(self):
        product = Product.objects.create(shop=self.shop, title='title', content='content')
        response = self.client.get(reverse('product-detail', kwargs={'pk': product.pk + 1}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Not found.'})

    def test_product_detail_when_product_exist_but_not_public_then_404(self):
        product = Product.objects.create(shop=self.shop, title='title', content='content', public=False)
        response = self.client.get(reverse('product-detail', kwargs={'pk': product.pk}))
        print(response.json())
        print(response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Not found.'})
