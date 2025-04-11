import re
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.cache import cache

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
    


class UserDetailSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    current_balance = serializers.ReadOnlyField(source='balance')
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'current_balance', 'is_active', 'date_joined']

    

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
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']

    def validate_name(self, value):
        '''
            Converts category name to lowercase
        '''
        # Trim, reduce multiple spaces to single space, and lowercase
        value = re.sub(r'\s+', ' ', value.strip()).lower()
        
        # Validate with regex
        pattern = r'^[a-z0-9\- ]{3,50}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Category name must be 3 to 50 characters long, and only include lowercase letters, numbers, dashes, and single spaces."
            )
        
        return value



class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']



class TransactionSerializer(serializers.ModelSerializer):
    '''
        Serializer for Transactions with validation of amount
    '''
    user_email = serializers.EmailField(source='user_id.email', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    category_name = serializers.StringRelatedField(source='category_id', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user_email', 'category_id', 'category_name', 'amount', 'type', 'description']

    def validate_amount(self, value):
        '''
            Ensure amount is positive before (It will convert to negative for expense).
        '''
        if value <= 0:
            raise ValidationError("Amount must be positive")
        return value
    
    def validate(self, data):
        '''
            converts expense to negative value and income to positive value
        '''
        type = data.get('type')
        amount = data.get('amount')
        if type == Transaction.EXPENSE and amount > 0:
            data['amount'] = -amount
        elif type == Transaction.INCOME and amount < 0:
            data['amount'] = abs(amount)

        return data
    
    def validate_description(self, value):
        if value and (len(value) < 3 or len(value) > 255):
            raise serializers.ValidationError("Description must be between 3 and 255 characters.")
        return value
    
    def create(self, validated_data):
        # Automatically set the user to request.user
        user = self.context['request'].user
        validated_data['user_id'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        '''
            Only description can be updated. Others are ignored.
        '''
        validated_data = {'description': validated_data.get('description', instance.description)}
        return super().update(instance, validated_data)
    
    def get_extra_kwargs(self):
        ''' When retrieve, update, delete transaction, It has an instance of transaction all fields except description are read_only '''
        kwargs = super().get_extra_kwargs()
        if self.instance:
            read_only_fields = ['id', 'category_id', 'amount', 'type']
            for fields in read_only_fields:
                kwargs[fields] = {'read_only': True}

        return kwargs

    

class TransactionDetailSerializer(serializers.ModelSerializer):
    
    user_id = serializers.StringRelatedField()
    category_id = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    user_info = UserDetailSerializer(source='user_id', read_only=True)
    category_info = CategoryDetailSerializer(source='category_id', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user_id', 'category_id', 'amount', 'type', 'description', 'user_info', 'category_info', 'created_at', 'updated_at']
