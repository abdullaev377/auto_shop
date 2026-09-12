import logging

from decimal import Decimal

from urllib import (
    error,
    parse,
    request,
)

from django.conf import settings


logger = logging.getLogger(__name__)


def send_order_notification(order):

    token = getattr(
        settings,
        'TELEGRAM_BOT_TOKEN',
        '',
    )

    chat_id = getattr(
        settings,
        'TELEGRAM_ADMIN_CHAT_ID',
        '',
    )

    if not token or not chat_id:
        logger.warning(
            'Telegram notification is disabled'
        )
        return False

    items = list(
        order.items
        .select_related('product')
        .all()
    )

    lines = [
        '🚗 NEW MOTIVE ORDER',
        '',
        f'Order ID: #{order.id}',
        (
            'Customer: '
            f'{order.user.get_full_name()} '
            'or order.user.username}'
        ),
        f'Username: @{order.user.username}',
        f'Phone: {order.phone_number or "-"}',
        f'Email: {order.user.email or "-"}',
        f'Address: {order.address}',
        f'Status: {order.status}',
        (
            'Date: '
            f'{order.created_at:%Y-%m-%d %H:%M UTC}'
        ),
        '',
        'CARS:',
    ]

    total = Decimal('0')

    for index, item in enumerate(
        items,
        start=1,
    ):

        product = item.product

        lines.extend([
            (
                f'{index}. '
                f'{product.brand} '
                f'{product.model_name}'
            ),
            (
                f'   Price: '
                f'{product.currency} '
                f'{product.price:,.2f}'
            ),
            f'   Quantity: {item.count}',
            (
                f'   Total: '
                f'{product.currency} '
                f'{item.total_price:,.2f}'
            ),
            '',
        ])

        total += item.total_price

    currency = (
        items[0].product.currency
        if items
        else ''
    )

    lines.append(
        f'GRAND TOTAL: '
        f'{currency} {total:,.2f}'
    )

    endpoint = (
        f'https://api.telegram.org/'
        f'bot{token}/sendMessage'
    )

    payload = parse.urlencode({
        'chat_id': chat_id,
        'text': '\n'.join(lines),
    }).encode()

    try:

        with request.urlopen(
            request.Request(
                endpoint,
                data=payload,
            ),
            timeout=15,
        ) as response:

            return response.status == 200

    except error.HTTPError as exc:

        logger.exception(
            'Telegram API returned HTTP %s '
            'for order %s',
            exc.code,
            order.id,
        )

    except (
        error.URLError,
        TimeoutError,
        OSError,
    ):

        logger.exception(
            'Telegram notification failed '
            'for order %s',
            order.id,
        )

    return False