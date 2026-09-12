from rest_framework.test import APITestCase

from accounts.models import CustomUser
from product.models import Product


class FavoriteOwnershipTests(APITestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(username='buyer', email='buyer@example.com', password='StrongPass123!', auth_type='via_email', auth_status='done')
		self.other = CustomUser.objects.create_user(username='other', email='other@example.com', password='StrongPass123!', auth_type='via_email', auth_status='done')
		self.product = Product.objects.create(title='Audi A4', short_desc='Sedan', desc='A sedan', price=30000, user=self.other, brand='Audi', model_name='A4', vin='TESTAUDIA42022001')

	def test_favorite_is_private_to_authenticated_user(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(f'/comment/saved/{self.product.id}/')
		self.assertEqual(response.status_code, 200)
		saved = self.client.get('/comment/saved/')
		self.assertEqual(len(saved.data), 1)
from django.test import TestCase

# Create your tests here.
