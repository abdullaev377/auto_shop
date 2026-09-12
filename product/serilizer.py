from rest_framework import serializers
from .models import Product, Image
from comment.models import Saved



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image', 'is_main')
        extra_kwargs = {'image': {'required': False}}


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'category', 'short_desc', 'desc', 'quantity',
                  'is_active', 'is_deleted', 'price', 'currency', 'user', 'brand',
                  'model_name', 'year', 'mileage', 'fuel_type', 'transmission',
                  'drive_type', 'body_type', 'color', 'engine_volume', 'horsepower',
                  'vin', 'condition', 'location', 'images', 'is_favorite', 'created_at')
        read_only_fields = ('id', 'slug', 'user', 'is_active', 'is_deleted', 'quantity', 'is_favorite', 'created_at')

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and Saved.objects.filter(user=request.user, product=obj).exists())

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        Image.objects.bulk_create([Image(product=product, **image) for image in images])
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        instance = super().update(instance, validated_data)
        if images is not None:
            instance.images.all().delete()
            Image.objects.bulk_create([Image(product=instance, **image) for image in images])
        return instance
        
        
        
