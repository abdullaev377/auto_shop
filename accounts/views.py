from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from shared.services.verification import (
    send_verification_code,
)

from .models import (
    CODE_VERIFY,
    DONE,
    NEW,
    CustomUser,
    VIA_EMAIL,
    VIA_PHONE,
)

from .serializer import (
    SignUpSerializer,
    ChangeInfoSerializer,
    ChangePhotoSerializer,
    LoginSerializer,
)


class SignUpView(CreateAPIView):

    permission_classes = [AllowAny]

    queryset = CustomUser.objects.all()

    serializer_class = SignUpSerializer


class CodeVerify(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        code = request.data.get('code')

        if not code:
            raise ValidationError({
                'code': (
                    'Verification code is required'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        self.check_code_verify(
            user,
            code,
        )

        return Response({
            'id': user.id,
            'auth_status': user.auth_status,
            'msg': 'Code verified',
            'token': user.token(),
        })

    @staticmethod
    def check_code_verify(user, code):

        verification = user.codes.filter(
            is_used=False,
            code=str(code).strip(),
            expire_time__gte=timezone.now(),
        ).first()

        if verification is None:
            raise ValidationError({
                'msg': (
                    'Code is incorrect or expired'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        verification.is_used = True

        verification.save(
            update_fields=['is_used']
        )

        user.auth_status = CODE_VERIFY

        user.save(
            update_fields=[
                'auth_status',
                'updated_at',
            ]
        )

        return True


class GetNewCodeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        self.check_active_code(user)

        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(
                VIA_EMAIL
            )

        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(
                VIA_PHONE
            )

        else:
            raise ValidationError({
                'msg': 'Invalid verification type',
                'status': status.HTTP_400_BAD_REQUEST,
            })

        try:
            send_verification_code(
                user,
                code,
            )

        except Exception:
            raise ValidationError({
                'msg': (
                    'Verification code could not be sent'
                ),
                'status': (
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            })

        return Response({
            'msg': 'Verification code sent',
            'status': status.HTTP_201_CREATED,
        })

    @staticmethod
    def check_active_code(user):

        active_code = user.codes.filter(
            is_used=False,
            expire_time__gte=timezone.now(),
        ).first()

        if active_code:
            raise ValidationError({
                'msg': (
                    'You already have an active '
                    'verification code'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        if user.auth_status != NEW:
            raise ValidationError({
                'msg': (
                    'A new verification code is '
                    'not available for this account'
                ),
                'status': status.HTTP_400_BAD_REQUEST,
            })

        return True


class ChangeInfoView(UpdateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = ChangeInfoSerializer

    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user


class TokenRefresh(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        refresh = request.data.get(
            'refresh'
        )

        if not refresh:
            raise ValidationError({
                'refresh': (
                    'Refresh token is required'
                )
            })

        try:
            token = RefreshToken(refresh)

        except Exception:
            raise ValidationError({
                'refresh': (
                    'Refresh token is invalid '
                    'or expired'
                )
            })

        return Response({
            'refresh': str(token),
            'access': str(token.access_token),
        })


class ChangePhotoView(UpdateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = ChangePhotoSerializer

    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'photo': (
                request.build_absolute_uri(
                    user.photo.url
                )
                if user.photo
                else None
            ),
            'auth_status': user.auth_status,
            'auth_type': user.auth_type,
        })


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            'user'
        ]

        tokens = user.token()

        return Response({
            'msg': 'Login successful',
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        })


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get(
            'refresh'
        )

        if not refresh_token:
            return Response(
                {
                    'detail': (
                        'Refresh token is required'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(
                refresh_token
            )

            token.blacklist()

        except Exception:
            return Response(
                {
                    'detail': (
                        'Refresh token is invalid '
                        'or expired'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'msg': 'Logout successful'
        })