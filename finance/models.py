import uuid
from django.db import models
from finance.utils import DateTimeMixin
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db.models import Q


class CustomSoftDeleteManager(UserManager, models.Manager):
    """
    Custom manager for filtering soft-deleted objects, with methods to include or exclusively retrieve deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        return super().get_queryset()
    
    def only_deleted(self):
        return super().get_queryset().filter(is_deleted=True)



class CustomUser(AbstractUser):
    """
    CustomUser model extends AbstractUser, uses email as the username field, supports soft delete, and provides balance calculation and restore functionality.
    """
    email = models.EmailField(unique=True)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomSoftDeleteManager()

    class Meta:
        verbose_name = "User"
        constraints = [
            models.UniqueConstraint(
                fields=["email", "is_active"],
                name="unique_email_activity_user",
                condition=Q(is_active=True),
            ),
        ]

    def __str__(self):
        return self.username
    
    def delete(self, hard=False, *args, **kwargs):
        """
        Overrides the delete method to perform soft delete by default; use delete(hard=True) for hard delete.
        """
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted=True
            self.save(update_fields=['is_deleted'])

    def restore(self):
        """Restore method to undo soft deletion of a transaction by setting is_deleted to False."""

        self.is_deleted=False
        self.save(update_fields=['is_deleted'])
    
    @property
    def balance(self):
        """Calculate and return the total balance by aggregating all user transactions."""

        total_amount = self.transactions.aggregate(total=models.Sum('amount'))['total']
        return total_amount or 0
    
    @property
    def monthly_income(self):
        return self.transactions.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def monthly_expense(self):
        return self.transactions.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
    


class Category(DateTimeMixin):
    """
    Category model representing a unique category with a name stored in lowercase, inheriting DateTimeMixin.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural='Categories'

    def save(self, *args, **kwargs):
        """Override save method to convert the category name to lowercase before saving."""
    
        self.name = self.name.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    



class Transaction(DateTimeMixin):
    """
    Transaction model represents financial transactions with soft-delete functionality, categorized by type, source, and user, ensuring income is positive and expenses are negative.
    """

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
        """
        Overrides the save method to ensure expense amounts are negative and income amounts are positive.
        """

        if self.type == self.EXPENSE and self.amount > 0:
            self.amount = -self.amount
        elif self.type == self.INCOME and self.amount < 0:
            self.amount = abs(self.amount)
        super().save(*args, **kwargs)   
    
    
    def delete(self, hard=False, *args, **kwargs):
        """
        Override the delete method to perform soft delete by default, and hard delete when `hard=True` is passed.
        """

        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])
    
    def restore(self):
        """
        Restore a soft-deleted transaction by setting is_deleted to False and saving the change.
        """

        self.is_deleted = False
        self.save(update_fields=['is_deleted'])

    def validate_description(self, value):
        """Validates that the description length is between 3 and 255 characters."""

        if value and (len(value) < 3 or len(value) > 255):
            raise ValidationError("Description must be between 3 and 255 characters.")
        return value



class PasswordReset(models.Model):
    """
    Model to store password reset tokens associated with user emails.
    """
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)