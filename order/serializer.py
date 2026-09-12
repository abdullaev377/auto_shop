from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(
    serializers.ModelSerializer
):

    product_title = serializers.CharField(
        source='product.title',
        read_only=True,
    )

    product_brand = serializers.CharField(
        source='product.brand',
        read_only=True,
    )

    product_model = serializers.CharField(
        source='product.model_name',
        read_only=True,
    )

    currency = serializers.CharField(
        source='product.currency',
        read_only=True,
    )

    price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = OrderItem

        fields = (
            'id',
            'product',
            'product_title',
            'product_brand',
            'product_model',
            'currency',
            'price',
            'count',
            'total_price',
        )


class OrderSerializer(
    serializers.ModelSerializer
):

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    total = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = (
            'id',
            'status',
            'address',
            'phone_number',
            'items',
            'total',
            'created_at',
        )

        read_only_fields = (
            'id',
            'status',
            'items',
            'total',
            'created_at',
        )

    def get_total(self, obj):

        return sum(
            (
                item.total_price
                for item in obj.items.all()
            ),
            start=0,
        )