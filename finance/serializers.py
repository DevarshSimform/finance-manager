from finance.models import CustomUser, Category, Transaction
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'balance', 'date_joined']

    # def validate_date_joined(self, value):
    #     if value > now():
    #         raise ValidationError("Date joined should be less than present date")
    #     return value
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user_id', 'category_id', 'amount', 'is_deleted', 'description', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if self.value <= 0:
            raise ValidationError("Amount must be positive")
        return value
