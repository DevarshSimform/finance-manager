from django.db import models

from finance.models import CustomUser


class Group(models.Model):

    name = models.CharField(max_length=30)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created')
    members = models.ManyToManyField(CustomUser, through='GroupMember')
    created_at = models.DateTimeField(auto_now_add=True)


class GroupMember(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)


class Expense(models.Model):

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_between = models.ManyToManyField(CustomUser, through='SplitExpense', related_name='split_expenses')
    created_at = models.DateTimeField(auto_now_add=True)


class SplitExpense(models.Model):

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)   # set amount divide by all user in expense
    is_settled = models.BooleanField(default=False)