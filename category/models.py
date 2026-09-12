from django.db import models
from shared.models import BaseModel
from django.utils.text import slugify
import uuid
# Create your models here.

class Category(BaseModel):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='child', null=True, blank=True)
    
    
    class Meta:
        verbose_name_plural = 'Categories'
        db_table  = 'category'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            temp_slug = f"{slugify(self.title)}-{str(uuid.uuid4())[-5:]}"
            while Category.objects.filter(slug = temp_slug).exists():
                temp_slug += str(uuid.uuid4())[-1]
            self.slug = temp_slug   
            
        super().save(*args, **kwargs)
        
    
    
    
    