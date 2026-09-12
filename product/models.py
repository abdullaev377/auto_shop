from django.db import models
from category.models import Category
from accounts.models import CustomUser
from django.utils.text import slugify
import uuid
from shared.models import BaseModel
# Create your models here.


class Product(BaseModel):
    FUEL_TYPES = (('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid'), ('electric', 'Electric'))
    TRANSMISSIONS = (('manual', 'Manual'), ('automatic', 'Automatic'))
    DRIVE_TYPES = (('fwd', 'Front-wheel drive'), ('rwd', 'Rear-wheel drive'), ('awd', 'All-wheel drive'))
    BODY_TYPES = (('sedan', 'Sedan'), ('suv', 'SUV'), ('hatchback', 'Hatchback'), ('wagon', 'Wagon'), ('coupe', 'Coupe'), ('convertible', 'Convertible'), ('van', 'Van'), ('pickup', 'Pickup'))
    CONDITIONS = (('new', 'New'), ('used', 'Used'))
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    short_desc = models.CharField(max_length=50)
    desc = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=80, default='Unknown', db_index=True)
    model_name = models.CharField(max_length=120, default='Unknown', db_index=True)
    year = models.PositiveIntegerField(default=2000, db_index=True)
    mileage = models.PositiveIntegerField(default=0, help_text='Mileage in kilometres', db_index=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, default='petrol', db_index=True)
    transmission = models.CharField(max_length=20, choices=TRANSMISSIONS, default='automatic')
    drive_type = models.CharField(max_length=10, choices=DRIVE_TYPES, blank=True)
    body_type = models.CharField(max_length=20, choices=BODY_TYPES, default='sedan', db_index=True)
    color = models.CharField(max_length=40, blank=True)
    engine_volume = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    horsepower = models.PositiveIntegerField(null=True, blank=True)
    vin = models.CharField(max_length=17, unique=True, null=True, blank=True)
    condition = models.CharField(max_length=10, choices=CONDITIONS, default='used')
    location = models.CharField(max_length=120, default='Unknown', db_index=True)
    
    
    class Meta:
        db_table  = 'product'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            temp_slug = f"{slugify(self.title)}-{str(uuid.uuid4())[-5:]}"
            while Product.objects.filter(slug = temp_slug).exists():
                temp_slug += str(uuid.uuid4())[-1]
            self.slug = temp_slug   
            
        super().save(*args, **kwargs)
        
        

class Image(BaseModel):
    image = models.ImageField(upload_to='product/', default='product/default.png')
    is_main = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    
    def __str__(self):
        return self.product.title
    
    class Meta:
        db_table = 'image'
        
        
        

        
        