from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from urllib import error, parse, request


class Command(BaseCommand):
    help = 'Send a Telegram configuration test message.'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
        if not token or not chat_id:
            raise CommandError('TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID must be configured.')
        endpoint = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = parse.urlencode({'chat_id': chat_id, 'text': 'Automotive marketplace Telegram test message.'}).encode()
        try:
            with request.urlopen(request.Request(endpoint, data=payload), timeout=10) as response:
                if response.status != 200:
                    raise CommandError(f'Telegram returned HTTP {response.status}.')
        except (error.URLError, TimeoutError, OSError) as exc:
            raise CommandError('Telegram request failed.') from exc
        self.stdout.write(self.style.SUCCESS('Telegram test message sent.'))