from rest_framework.test import APITestCase
from unittest.mock import patch

from accounts.models import CustomUser
from order.models import Order
from product.models import Product
from category.models import Category
from card.models import Card, CardItem


class OrderOwnershipTests(APITestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(username='buyer', email='buyer@example.com', password='StrongPass123!', auth_type='via_email', auth_status='done')
		self.other = CustomUser.objects.create_user(username='other', email='other@example.com', password='StrongPass123!', auth_type='via_email', auth_status='done')
		self.order = Order.objects.create(user=self.other, address='Private address', status='new')

	def test_user_cannot_read_another_users_order(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.get(f'/order/{self.order.id}/')
		self.assertEqual(response.status_code, 404)

	def test_checkout_calculates_total_and_survives_telegram_failure(self):
		product = Product.objects.create(
			title='BMW X5', short_desc='SUV', desc='Test car', price=50000,
			quantity=2, user=self.other, category=Category.objects.create(title='Checkout SUV'),
			brand='BMW', model_name='X5', year=2022, body_type='suv', vin='ORDERBMWX5202201',
		)
		card = Card.objects.create(user=self.user)
		CardItem.objects.create(card=card, product=product, count=2)
		self.client.force_authenticate(user=self.user)
		with patch('order.views.send_order_notification', return_value=False):
			response = self.client.post('/order/', {'address': 'Test address'}, format='json')
		self.assertEqual(response.status_code, 201)
		order = Order.objects.get(user=self.user)
		self.assertEqual(str(order.items.get().total_price), '100000.00')
		self.assertEqual(Product.objects.get(pk=product.pk).quantity, 0)
from django.test import TestCase

# Create your tests here.
