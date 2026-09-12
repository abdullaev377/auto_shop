from django.db import models
from accounts.models import CustomUser
from product.models import Product
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    text = models.TextField()
    rating = models.IntegerField(validators=[
                MinValueValidator(0),
                MaxValueValidator(5)
            ], default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating}★)"
    
    
    
class Saved(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} saved {self.product}"
    
    
    
class ProductView(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_views')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} viewed {self.product}"
    
    class Meta:
        unique_together = ('user', 'product')
    
    

class RecentlyViews(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_recendly')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
    
