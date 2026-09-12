from django.db import models
from accounts.models import CustomUser
from product.models import Product
from shared.models import BaseModel

# Create your models here.

class Card(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    

class CardItem(BaseModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    count = models.PositiveBigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('card', 'product'), name='unique_card_product'),
        ]
    
    

   