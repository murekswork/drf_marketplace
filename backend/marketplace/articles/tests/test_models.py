from articles.models import Article
from django.contrib.auth import get_user_model
from django.test import TestCase
from order.models import Order
from products.models import Product
from shop.models import Shop


class ArticleModelTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test', email='test@mail.com'
        )
        self.shop = Shop.objects.create(
            user=self.user, title='title', description='description'
        )
        self.product = Product.objects.create(
            shop=self.shop, title='title', public=True, content='content', quantity=5
        )
        self.order = Order.objects.create(product=self.product, count=3, user=self.user)
        self.article1 = Article.objects.create(
            user=self.user,
            title='title',
            article_content='article content',
            published=True,
            mark=5,
            order=self.order,
            product=self.product,
        )

    def test_article_fields_title_after_creation(self):
        self.assertTrue(self.article1.title == 'title')

    def test_article_fields_content_after_creation(self):
        self.assertTrue(self.article1.article_content == 'article content')

    def test_article_fields_user_after_creation(self):
        self.assertTrue(self.article1.user == self.user)

    def test_article_fields_product_after_creation(self):
        self.assertTrue(self.article1.product == self.product)

    def test_article_fields_mark_after_creation(self):
        self.assertTrue(self.article1.published is True)

    def test_article_fields_published_after_creation(self):
        self.assertTrue(self.article1.mark == 5)

    def test_article_model_when_first_article_create_then_product_mark_changes(self):
        self.assertTrue(self.product.mark == 5)

    def test_article_model_when_second_article_create_then_product_mark_changes(self):
        self.article2 = Article.objects.create(
            user=self.user,
            title='title',
            article_content='article content',
            published=True,
            mark=1,
            order=self.order,
            product=self.product,
        )
        self.assertTrue(self.product.mark == (5 + 1) / 2)

    def test_article_model_when_second_article_change_then_product_mark_changes(self):
        self.article1.mark = 1
        self.article1.save()
        self.assertTrue(self.product.mark == 1)
