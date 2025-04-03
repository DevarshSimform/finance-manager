from finance.models import CustomUser, Category, Transaction
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        '''
            
        '''
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        # here we accept password from client but not sending it into response by setting write-only is True
        extra_kwargs = {
            'passowrd': {'write_only': True},
        }

    def create(self, validated_data):
        '''
            create_user hashes the passwrod using django's authentication system
        '''
        user = CustomUser.objects.create_user(**validated_data)
        return user
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']

    def validate_name(self, value):
        '''
            Converts category name to lowercase
        '''
        return value.lower()


class TransactionSerializer(serializers.ModelSerializer):
    '''
        
    '''
    class Meta:
        model = Transaction
        fields = ['id', 'user_id', 'category_id', 'amount', 'type', 'description', 'created_at', 'updated_at']

    def validate_amount(self, value):
        '''
            Ensure amount is positive before (It will convert to negative for expense).
        '''
        if value <= 0:
            raise ValidationError("Amount must be positive")
        return value
    
    def validate(self, data):
        '''
            converts expense to negative value and inclome to positive value
        '''
        transaction_type = data.get('type')
        amount = data.get('amount')

        if transaction_type == Transaction.EXPENSE and amount > 0:
            data['amount'] = -amount
        elif transaction_type == Transaction.INCOME and amount < 0:
            data['amount'] = abs(amount)
        
        return data
    
    def update(self, instance, validated_data):
        '''
            Override update method to store expense as negative and income as positive while perform update
        '''
        transaction_type = validated_data.get('type')
        amount = validated_data.get('amount')

        if transaction_type == Transaction.EXPENSE and amount > 0:
            validated_data['amount'] = -amount
            print(amount)
        elif transaction_type == Transaction.INCOME and amount < 0:
            validated_data['amount'] = abs(amount)

        return super().update(instance, validated_data)
    