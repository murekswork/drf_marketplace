from django.db import models
from django.utils.text import slugify


class Category(models.Model):

    title = models.CharField(max_length=120, unique=True, default='Category Name')
    description = models.TextField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=120, null=True, blank=True)

    def __str__(self):
        return f'Category: {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)