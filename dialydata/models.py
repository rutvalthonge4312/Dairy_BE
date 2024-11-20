from django.db import models
from useronbording.models import User

# Create your models here.
class DailyDairyEntry(models.Model):

    STATUS_CHOICES = [
        ('M', 'Morning'),
        ('E', 'Evening'),
    ]
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE,)
    date=models.DateField(null=False)
    milk_rate=models.IntegerField(null=False,default=0)
    milk_quantity=models.IntegerField(null=False,default=0)
    shift= models.CharField(max_length=1, choices=STATUS_CHOICES, default='M')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=200)