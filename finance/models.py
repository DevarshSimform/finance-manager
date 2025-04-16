import uuid
from django.db import models
from finance.utils import DateTimeMixin
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.contrib.auth.models import UserManager 
from django.core.exceptions import ValidationError


class CustomSoftDeleteManager(UserManager, models.Manager):
    '''
        Custom manager to filter soft delete every time. It inherits UserManager to use create_user() in CustomUser.objects.create_user()
    '''
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        return super().get_queryset()
    
    def only_deleted(self):
        return super().get_queryset().filter(is_deleted=True)



class CustomUser(AbstractUser):
    '''
        here, email is username_field by-default it is username but we consider email as uesrname_field. It has soft-delete
    '''
    email = models.EmailField(unique=True)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomSoftDeleteManager()

    def __str__(self):
        return self.username
    
    def delete(self, hard=False, *args, **kwargs):
        '''
            Override the delete method, default delete() will perform soft delete. To hard delete use delete(hard=True).
        '''
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted=True
            self.save(update_fields=['is_deleted'])

    def restore(self):
        '''
            restore method is used to restore soft deleted transaction.
        '''
        self.is_deleted=False
        self.save(update_fields=['is_deleted'])
    
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
            Override save method to save category name into lowercase
        '''
        self.name = self.name.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    



class Transaction(DateTimeMixin):
    '''
        Transactions table has all transactions, soft-delete implemented. Every transaction has user_id and category_id. amount is stored as per transaction type.
    '''
    def get_other_category():
        return Category.objects.get_or_create(name='other')[0]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    category_id = models.ForeignKey(Category, on_delete=models.SET(get_other_category), related_name='has', default='other')

    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSACTION_CHOICES = {
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    }

    CASH = 'cash'
    CARD = 'card'
    BANK_PAYMENT = 'bank_payment'
    SOURCE_CHOICES = {
        (CASH, 'Cash'),
        (CARD, 'Card'),
        (BANK_PAYMENT, 'Bank_Payment')
    }

    source = models.CharField(max_length=12, choices=SOURCE_CHOICES, default=CASH)
    type = models.CharField(max_length=7, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    objects = CustomSoftDeleteManager()

    def __str__(self):
        return f"{self.type} - {self.amount}"

    def save(self, *args, **kwargs):
        '''
            Ensure that expense amount should be negative and income is positive 
        '''
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

    def validate_description(self, value):
        if value and (len(value) < 3 or len(value) > 255):
            raise ValidationError("Description must be between 3 and 255 characters.")
        return value

    # @classmethod
    # def get_user_balance(cls, user_id):
    #     '''
    #         Another approach to find user's balance but It is class dependent.
    #     '''
    #     total_amount = cls.objects.filter(user_id=user_id, is_deleted=False).aggregate(total=models.Sum('amount'))['total']
    #     return total_amount or 0  



class PasswordReset(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)