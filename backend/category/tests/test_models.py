from django.db import IntegrityError
from django.test import TestCase

from category.models import Category

class CategoryModelTestCase(TestCase):

    def setUp(self):
        self.category1 = Category.objects.create(title='category1', description='description1')
        self.category2 = Category.objects.create(title='category2', description='description2')


    def test_str(self):
        self.assertEquals(self.category1.__str__(), 'Category: category1')
        self.assertEquals(self.category2.__str__(), 'Category: category2')

    def test_title_field(self):
        self.assertEqual(self.category1.title, 'category1')
        self.assertEqual(self.category2.title, 'category2')

    def test_description_field(self):
        self.assertEqual(self.category1.description, 'description1')
        self.assertEqual(self.category2.description, 'description2')

    def test_slug_field(self):
        self.assertEqual(self.category1.slug, 'category1')
        self.assertEqual(self.category2.slug, 'category2')

    def test_title_field_unique(self):
        with self.assertRaises(IntegrityError):
            category1_copy = Category.objects.create(title='category1', description='description1')
            category2_copy = Category.objects.create(title='category2', description='description2')
