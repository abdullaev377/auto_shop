from rest_framework import serializers
from .models import Card, CardItem


class CardItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CardItem
        fields = ('id', 'product', 'product_title', 'price', 'count')


class CardSerializer(serializers.ModelSerializer):
    items = CardItemSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = ('id', 'items')