from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from .services.telegram import send_order_notification


class TelegramServiceTests(SimpleTestCase):
	def setUp(self):
		product = SimpleNamespace(title='BMW X5', currency='EUR', price=Decimal('50000.00'))
		item = SimpleNamespace(product=product, count=1, total_price=product.price)
		self.order = SimpleNamespace(
			id='order-123', user=SimpleNamespace(username='driver', email='driver@example.com', get_full_name=lambda: 'Driver'),
			phone_number='', status='pending', created_at=datetime.now(timezone.utc),
			items=SimpleNamespace(select_related=lambda *args: [item], exists=lambda: True, first=lambda: item),
		)

	@override_settings(TELEGRAM_BOT_TOKEN='', TELEGRAM_ADMIN_CHAT_ID='')
	def test_missing_configuration_is_safe(self):
		with patch('shared.services.telegram.request.urlopen') as urlopen:
			self.assertFalse(send_order_notification(self.order))
		urlopen.assert_not_called()

	@override_settings(TELEGRAM_BOT_TOKEN='test-token', TELEGRAM_ADMIN_CHAT_ID='test-chat')
	def test_successful_notification(self):
		response = MagicMock(status=200)
		response.__enter__.return_value = response
		with patch('shared.services.telegram.request.urlopen', return_value=response) as urlopen:
			self.assertTrue(send_order_notification(self.order))
		self.assertIn(b'order-123', urlopen.call_args.args[0].data)

	@override_settings(TELEGRAM_BOT_TOKEN='test-token', TELEGRAM_ADMIN_CHAT_ID='test-chat')
	def test_api_failure_is_safe(self):
		with patch('shared.services.telegram.request.urlopen', side_effect=TimeoutError):
			self.assertFalse(send_order_notification(self.order))

# Create your tests here.
