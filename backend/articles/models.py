from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.manager import Manager
from order.models import Order
from products.models import Product


class ArticleQuerySet(models.QuerySet):

    def is_not_published(self):
        return self.filter(published=False)

    def is_published(self):
        return self.filter(published=True)


class ArticleManager(Manager):

    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self, *args, **kwargs):
        return self.get_queryset().is_published()

    def get_published_queryset(self):
        return self.get_queryset().filter(published=False)


class Article(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_DEFAULT, default=0)
    title = models.CharField(max_length=120, blank=False, null=False, unique=True, default='Article title')
    article_content = models.TextField(max_length=512, default='Article body', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    published = models.BooleanField(default=True)

    mark = models.IntegerField(default=5, choices=(
        (1, 'Awfull'),
        (2, 'Bad'),
        (3, 'Not bad'),
        (4, 'Good'),
        (5, 'Excellent'))
    )

    objects = ArticleManager()

    @property
    def content(self):
        return self.article_content

    def __str__(self):
        return f'Article {self.pk} with name: {self.title}'
# Create your models here.
