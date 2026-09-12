from django.contrib import admin
from .models import Comment, Saved, ProductView, RecentlyViews

admin.site.register(Comment)
admin.site.register(Saved)
admin.site.register(ProductView)
admin.site.register(RecentlyViews)

# Register your models here.
