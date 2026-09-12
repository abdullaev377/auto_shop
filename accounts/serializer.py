from django.contrib.auth import authenticate
from django.db.models import Q

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from shared.services.verification import (
    send_verification_code,
)

from shared.utils import check_email_or_phone

from .models import (
    CustomUser,
    VIA_EMAIL,
    VIA_PHONE,
    CODE_VERIFY,
    NEW,
    DONE,
    PHOTO_DONE,
)


class SignUpSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_input'] = serializers.CharField(
            required=False,
            write_only=True,
        )

        self.fields['email_or_phone_number'] = serializers.CharField(
            required=False,
            write_only=True,
        )

        self.fields['password'] = serializers.CharField(
            required=True,
            write_only=True,
            min_length=8,
        )

        self.fields['conf_password'] = serializers.CharField(
            required=False,
            write_only=True,
        )

    class Meta:
        model = CustomUser

        fields = [
            'id',
            'auth_status',
            'auth_type',
        ]

        read_only_fields = [
            'id',
            'auth_status',
            'auth_type',
        ]

    def create(self, validated_data):
        validated_data.pop(
            'conf_password',
            None,
        )

        user = super().create(
            validated_data
        )

        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(
                VIA_EMAIL
            )

        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(
                VIA_PHONE
            )

        else:
            user.delete()

            raise ValidationError({
                'msg': 'Invalid email or phone number',
                'status': status.HTTP_400_BAD_REQUEST,
            })

        try:
            send_verification_code(
                user,
                code,
            )

        except Exception:
            user.delete()

            raise ValidationError({
                'msg': (
                    'Verification code could not be sent. '
                    'Check server email/SMS settings.'
                ),
                'status': (
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            })

        return user

    def validate(self, data):
        user_input = (
            data.get('user_input')
            or data.get('email_or_phone_number')
        )

        data.pop(
            'user_input',
            None,
        )

        if not user_input:
            raise ValidationError({
                'user_input': (
                    'Email or phone number is required'
                )
            })

        if (
            data.get('conf_password')
            and data.get('password')
            != data.get('conf_password')
        ):
            raise ValidationError({
                'conf_password': (
                    'Passwords do not match'
                )
            })

        normalized_input = (
            str(user_input)
            .strip()
            .lower()
        )

        existing = CustomUser.objects.filter(
            Q(email=normalized_input)
            | Q(phone_number=normalized_input)
        ).first()

        if (
            existing
            and existing.auth_status
            not in [NEW, CODE_VERIFY]
        ):
            raise ValidationError({
                'user_input': (
                    'This email or phone number '
                    'is already registered'
                )
            })

        if existing:
            existing.delete()

        data['email_or_phone_number'] = (
            normalized_input
        )

        return self.auth_validate(data)

    @staticmethod
    def auth_validate(data):
        user_input = (
            str(
                data.get(
                    'email_or_phone_number'
                )
            )
            .strip()
            .lower()
        )

        data.pop(
            'email_or_phone_number',
            None,
        )

        user_auth_type = check_email_or_phone(
            user_input
        )

        if user_auth_type == 'email':
            data['email'] = user_input
            data['auth_type'] = VIA_EMAIL

        elif user_auth_type == 'phone':
            data['phone_number'] = user_input
            data['auth_type'] = VIA_PHONE

        else:
            raise ValidationError({
                'msg': (
                    'Invalid email or phone number'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        return data

    def to_representation(self, instance):
        data = super().to_representation(
            instance
        )

        data.update(
            instance.token()
        )

        return data


class ChangeInfoSerializer(serializers.Serializer):

    first_name = serializers.CharField(
        required=True,
        write_only=True,
    )

    last_name = serializers.CharField(
        required=True,
        write_only=True,
    )

    username = serializers.CharField(
        required=True,
        write_only=True,
    )

    email = serializers.EmailField(
        required=False,
        write_only=True,
    )

    phone_number = serializers.CharField(
        required=False,
        write_only=True,
    )

    password = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    conf_password = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    def validate(self, data):
        password = data.get('password')
        conf_password = data.get('conf_password')

        if password and password != conf_password:
            raise ValidationError({
                'msg': 'Passwords do not match',
                'status': status.HTTP_400_BAD_REQUEST,
            })

        return data

    def update(self, instance, validated_data):

        if instance.auth_status == NEW:
            raise ValidationError({
                'msg': (
                    'You have not verified '
                    'your account yet'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        instance.first_name = validated_data.get(
            'first_name',
            instance.first_name,
        )

        instance.last_name = validated_data.get(
            'last_name',
            instance.last_name,
        )

        instance.username = validated_data.get(
            'username',
            instance.username,
        )

        if validated_data.get('email'):
            instance.email = (
                validated_data['email'].lower()
            )

        if validated_data.get('phone_number'):
            instance.phone_number = (
                validated_data['phone_number']
            )

        password = validated_data.get('password')

        if password:
            instance.set_password(password)

        instance.auth_status = DONE

        instance.save()

        return instance

    def to_representation(self, instance):
        return {
            'msg': 'Information updated',
            'status': status.HTTP_200_OK,
            'token': instance.token(),
        }


class ChangePhotoSerializer(serializers.Serializer):

    photo = serializers.ImageField()

    def update(self, instance, validated_data):

        if validated_data.get('photo'):
            instance.photo = validated_data['photo']

        instance.auth_status = PHOTO_DONE

        instance.save()

        return instance

    def to_representation(self, instance):
        return {
            'msg': 'Photo updated',
            'status': status.HTTP_200_OK,
            'token': instance.token(),
        }


class LoginSerializer(serializers.Serializer):

    user_input = serializers.CharField(
        required=True,
        write_only=True,
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):

        user_input = str(
            attrs.get('user_input', '')
        ).strip()

        password = attrs.get('password')

        user = CustomUser.objects.filter(
            Q(username__iexact=user_input)
            | Q(email__iexact=user_input)
            | Q(phone_number=user_input)
        ).first()

        if not user:
            raise ValidationError({
                'msg': (
                    'Login or password is incorrect'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        if user.auth_status in [
            NEW,
            CODE_VERIFY,
        ]:
            raise ValidationError({
                'msg': (
                    'Please complete registration '
                    'verification first'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        authenticated_user = authenticate(
            username=user.username,
            password=password,
        )

        if not authenticated_user:
            raise ValidationError({
                'msg': (
                    'Login or password is incorrect'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        attrs['user'] = authenticated_user

        return attrs