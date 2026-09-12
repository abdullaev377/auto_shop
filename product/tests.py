from rest_framework.test import APITestCase

from accounts.models import CustomUser
from category.models import Category
from .models import Product


class ProductApiTests(APITestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(username='seller', email='seller@example.com', password='StrongPass123!', auth_type='via_email', auth_status='done', user_role='seller')
		self.category = Category.objects.create(title='SUV')
		self.product = Product.objects.create(title='BMW X5', short_desc='SUV', desc='A tested SUV', price=50000, user=self.user, brand='BMW', model_name='X5', year=2022, mileage=12000, body_type='suv', category=self.category, vin='TESTBMWX52022001')

	def test_list_search_is_paginated(self):
		response = self.client.get('/product/?search=BMW')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['id'], str(self.product.id))

	def test_uuid_detail_route_returns_product(self):
		response = self.client.get(f'/product/{self.product.id}/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['product']['brand'], 'BMW')
from django.test import TestCase

# Create your tests here.
