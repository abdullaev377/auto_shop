from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'parent')
	search_fields = ('title',)
	list_filter = ('parent',)
