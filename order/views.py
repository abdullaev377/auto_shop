import logging

from django.db import transaction

from rest_framework import (
    permissions,
    status,
)

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import MANAGER
from card.models import Card
from product.models import Product

from shared.services.telegram import (
    send_order_notification,
)

from .models import Order, OrderItem
from .serializer import OrderSerializer


logger = logging.getLogger(__name__)


class OrderListCreateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):

        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related(
                'items__product'
            )
            .order_by('-created_at')
        )

        return Response(
            OrderSerializer(
                orders,
                many=True,
            ).data
        )

    @transaction.atomic
    def post(self, request):

        address = str(
            request.data.get('address') or ''
        ).strip()

        phone_number = str(
            request.data.get(
                'phone_number'
            )
            or request.user.phone_number
            or ''
        ).strip()

        if not address:
            return Response(
                {
                    'detail': (
                        'Address is required'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not phone_number:
            return Response(
                {
                    'detail': (
                        'Phone number is required'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        card = (
            Card.objects
            .select_for_update()
            .filter(user=request.user)
            .first()
        )

        if not card or not card.items.exists():
            return Response(
                {
                    'detail': (
                        'Your cart is empty'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = list(
            card.items
            .select_related('product')
            .all()
        )

        product_ids = [
            item.product_id
            for item in items
        ]

        locked_products = {
            product.id: product
            for product in (
                Product.objects
                .select_for_update()
                .filter(
                    id__in=product_ids
                )
            )
        }

        for item in items:

            product = locked_products.get(
                item.product_id
            )

            if (
                product is None
                or not product.is_active
                or product.is_deleted
                or item.count > product.quantity
            ):
                title = (
                    product.title
                    if product
                    else 'A cart item'
                )

                return Response(
                    {
                        'detail': (
                            f'{title} is '
                            'no longer available'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = Order.objects.create(
            user=request.user,
            address=address,
            phone_number=phone_number,
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=locked_products[
                    item.product_id
                ],
                count=item.count,
                total_price=(
                    locked_products[
                        item.product_id
                    ].price * item.count
                ),
            )
            for item in items
        ])

        for item in items:

            product = locked_products[
                item.product_id
            ]

            product.quantity -= item.count

            product.save(
                update_fields=[
                    'quantity',
                    'updated_at',
                ]
            )

        card.items.all().delete()

        order = (
            Order.objects
            .prefetch_related(
                'items__product'
            )
            .get(pk=order.pk)
        )

        try:
            send_order_notification(
                order
            )

        except Exception:
            logger.exception(
                'Telegram notification failed '
                'for order %s',
                order.id,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, pk):

        order = (
            Order.objects
            .filter(
                pk=pk,
                user=request.user,
            )
            .prefetch_related(
                'items__product'
            )
            .first()
        )

        if order is None:
            return Response(
                {
                    'detail': (
                        'Order not found'
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            OrderSerializer(order).data
        )


class OrderStatusView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def patch(self, request, pk):

        if request.user.user_role != MANAGER:
            return Response(
                {
                    'detail': (
                        'Manager access required'
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        order = Order.objects.filter(
            pk=pk
        ).first()

        if order is None:
            return Response(
                {
                    'detail': (
                        'Order not found'
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get(
            'status'
        )

        valid_statuses = {
            value
            for value, _ in Order.STATUS
        }

        if new_status not in valid_statuses:
            return Response(
                {
                    'detail': (
                        'Invalid order status'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status

        order.save(
            update_fields=[
                'status',
                'updated_at',
            ]
        )

        return Response(
            OrderSerializer(order).data
        )