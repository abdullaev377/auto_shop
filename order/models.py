from django.db import models
from accounts.models import CustomUser
from product.models import Product
from shared.models import BaseModel

    
class Order(BaseModel):
    STATUS = (
        ('pending', 'PENDING'),
        ('confirmed', 'CONFIRMED'),
        ('processing', 'PROCESSING'),
        ('completed', 'COMPLETED'),
        ('cancelled', 'CANCELLED'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    address = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    count = models.PositiveBigIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    