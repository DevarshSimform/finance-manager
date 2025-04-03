import uuid
from django.db import models
from finance.utils import DateTimeMixin
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
    @property
    def balance(self):
        '''
            here we have to fetch all transactions of user by backward relationship
        '''
        total_amount = self.transactions.aggregate(total=models.Sum('amount'))['total']
        return total_amount or 0
    


class Category(DateTimeMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural='Categories'

    def save(self, *args, **kwargs):
        '''
            override save method to save category name into lowercase
        '''
        self.name = self.name.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    



class TransactionManager(models.Manager):
    '''
        Custom manager to filter soft delete every time
    '''
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        return super().get_queryset()
    
    def only_deleted(self):
        return super().get_queryset().filter(is_deleted=True)


class Transaction(DateTimeMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='has')

    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSACTION_CHOICES = {
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    }

    type = models.CharField(max_length=7, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    objects = TransactionManager()

    def __str__(self):
        return f"{self.type} - {self.amount}"


    def save(self, *args, **kwargs):
        if self.type == self.EXPENSE and self.amount > 0:
            self.amount = -self.amount
        elif self.type == self.INCOME and self.amount < 0:
            self.amount = abs(self.amount)
        super().save(*args, **kwargs)   
    
    
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

    # @classmethod
    # def get_user_balance(cls, user_id):
    #     total_amount = cls.objects.filter(user_id=user_id, is_deleted=False).aggregate(total=models.Sum('amount'))['total']
    #     return total_amount or 0  