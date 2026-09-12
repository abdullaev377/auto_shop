import requests

from django.conf import settings
from django.core.mail import send_mail


def send_email_code(email, code):
    send_mail(
        subject='MOTIVE verification code',
        message=(
            f'Your MOTIVE verification code is: {code}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def get_eskiz_token():
    response = requests.post(
        'https://notify.eskiz.uz/api/auth/login',
        data={
            'email': settings.ESKIZ_EMAIL,
            'password': settings.ESKIZ_PASSWORD,
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()['data']['token']


def send_sms_code(phone_number, code):
    token = get_eskiz_token()

    response = requests.post(
        'https://notify.eskiz.uz/api/message/sms/send',
        headers={
            'Authorization': f'Bearer {token}',
        },
        data={
            'mobile_phone': phone_number,
            'message': (
                f'MOTIVE verification code: {code}'
            ),
            'from': settings.ESKIZ_FROM,
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def send_verification_code(user, code):
    if user.auth_type == 'via_email':
        send_email_code(
            user.email,
            code,
        )

    elif user.auth_type == 'via_phone':
        send_sms_code(
            user.phone_number,
            code,
        )

    else:
        raise ValueError(
            'Unknown verification type'
        )