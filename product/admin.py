from django.contrib import admin
from .models import Product, Image


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('title', 'brand', 'model_name', 'year', 'price', 'location', 'is_active')
	search_fields = ('title', 'brand', 'model_name', 'vin', 'location')
	list_filter = ('brand', 'fuel_type', 'transmission', 'body_type', 'condition', 'is_active')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
	list_display = ('product', 'is_main')
	search_fields = ('product__title',)
	list_filter = ('is_main',)

# Register your models here.
