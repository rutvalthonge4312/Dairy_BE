from django.db import models
from account.models import Account

# Create your models here.
class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'deposit'),
        ('WITHDRAWAL', 'withdrawal'),
    ]
    TRANSACTION_STATUS = [
        ('SUCCESS', 'success'),
        ('FAILED', 'failed'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=10, choices=TRANSACTION_STATUS)
    def __str__(self):
        return f'{self.transaction_type} of {self.amount} on {self.date}'
