from rest_framework.test import APITestCase

from .models import CustomUser


class AuthenticationTests(APITestCase):
	def test_signup_accepts_password_and_returns_tokens(self):
		response = self.client.post('/auth/signup', {
			'email_or_phone_number': 'driver@example.com',
			'password': 'StrongPass123!',
			'conf_password': 'StrongPass123!',
		}, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertIn('access', response.data)
		self.assertTrue(CustomUser.objects.filter(email='driver@example.com').exists())

	def test_profile_is_private(self):
		user = CustomUser.objects.create_user(username='driver', email='driver2@example.com', password='StrongPass123!', auth_type='via_email', auth_status='done')
		self.client.force_authenticate(user=user)
		response = self.client.get('/auth/profile')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['email'], user.email)
from django.test import TestCase

# Create your tests here.
