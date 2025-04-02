import uuid
from django.db import models
from finance.utils import DateTimeMixin
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    


class Category(DateTimeMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    INCOME = 'income'
    EXPENSE = 'expense'
    CATEGORY_CHOICES = {
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    }
    type = models.CharField(max_length=7, choices=CATEGORY_CHOICES)

    class Meta:
        verbose_name_plural='Categories'
    
    def __str__(self):
        return self.name
    



class TransactionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Transaction(DateTimeMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='has')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.description:
            return self.description
        else:
            return self.id
    
    def delete(self, hard=False, *args, **kwargs):
        '''
            Override the delete method, default delete() will perform soft delete. To hard delete use delete(hard=True).
        '''
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])
    
    def restore(self):
        '''
            restore method is used to restore soft deleted transaction.
        '''
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])
