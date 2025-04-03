from django.contrib.auth import authenticate

from finance.models import CustomUser, Category, Transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    '''
        Serializer for user registration
    '''
    # here we accept password from client but not sending it into response by setting write-only is True
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        '''
            create_user hashes the passwrod using django's authentication system
        '''
        user = CustomUser.objects.create_user(**validated_data)
        return user
    

class LoginSerializer(serializers.Serializer):
    '''
        Serializer for user login
    '''
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        '''
            To validate login credentials (email, password)
        '''
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Invalid email or password")
        
        refresh = RefreshToken.for_user(user)
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh), 
        }



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
    
    