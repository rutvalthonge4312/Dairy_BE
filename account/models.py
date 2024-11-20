from django.db import models
from useronbording.models import User
from django.core.exceptions import ValidationError


def validate_length_4(value):
    if len(value) != 4:
        raise ValidationError(
            'This field must be exactly 4 characters long.',
            params={'value': value},
        )
        
class Account(models.Model):
    ACCOUNT_TYPES = [
        ('Saving', 'saving'),
        ('Current', 'current'),
    ]
    bank_name=models.CharField(max_length=200)
    m_pin=models.CharField(max_length=4, validators=[validate_length_4])
    account_number = models.CharField(max_length=20,unique=True)
    account_type = models.CharField(max_length=50,choices=ACCOUNT_TYPES,null=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')

    def __str__(self):
        return f'Account {self.account_number} ({self.account_type})'

