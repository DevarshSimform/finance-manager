from django.db import models
from django.utils.timezone import now
from finance.models import CustomUser, Category


class TransactionLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    id = models.AutoField(primary_key=True)  # Auto-increment log entry ID
    transaction = models.CharField(default='None')
    user = models.CharField(default='None')
    category = models.CharField(default='None')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=7)  # 'income' or 'expense'
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    description = models.TextField(null=True, blank=True)
    logged_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.action.title()} - {self.transaction}"
        
