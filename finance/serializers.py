import re
from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from finance.models import (
    CustomUser, 
    Category, 
    Transaction
)

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, handling user creation and ensuring the password is write-only.
    """

    # here we accept password from client but not sending it into response by setting write-only is True
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for user details, including fields like id, username, email, current balance, active status, and date joined.
    """
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    current_balance = serializers.ReadOnlyField(source='balance')
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'current_balance', 'is_active', 'date_joined'] 

    

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login, validates credentials, updates last login, and returns user details with JWT tokens.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Invalid email or password")
        user.last_login = timezone.now()
        user.save()
        
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
    """
    CategorySerializer is a Django REST Framework serializer for the Category model, handling serialization, deserialization, custom validation for the `name` field, and formatting for `created_at` and `updated_at` fields.
    """
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Validates and formats a category name to lowercase, ensuring it meets length and character requirements.
        """
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
    """
    Serializer for detailed representation of the Category model, including 'id' and 'name' fields.
    """
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
        fields = ['id', 'user_email', 'category_id', 'category_name', 'amount', 'type', 'source', 'description']

    def validate_amount(self, value):
        """Validate that the amount is positive; raise ValidationError if not."""
        if value <= 0:
            raise ValidationError("Amount must be positive")
        return value
    
    def validate(self, data):
        """
        Validates and adjusts the transaction amount based on its type (expense or income).
        """
        type = data.get('type')
        amount = data.get('amount')
        if type == Transaction.EXPENSE and amount > 0:
            data['amount'] = -amount
        elif type == Transaction.INCOME and amount < 0:
            data['amount'] = abs(amount)

        return data
    
    def validate_description(self, value):
        """
        Validates that the description length is between 3 and 255 characters.
        """
        if value and (len(value) < 3 or len(value) > 255):
            raise serializers.ValidationError("Description must be between 3 and 255 characters.")
        return value
    
    def create(self, validated_data):
        # Automatically set the user to request.user
        user = self.context['request'].user
        validated_data['user_id'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Updates only the description field of the instance, ignoring other fields.
        """
        validated_data = {'description': validated_data.get('description', instance.description)}
        return super().update(instance, validated_data)
    
    def get_extra_kwargs(self):
        """
        Override get_extra_kwargs to make specific fields read-only when an instance is present (e.g., during retrieve, update, or delete operations).
        """
        kwargs = super().get_extra_kwargs()
        if self.instance:
            read_only_fields = ['id', 'category_id', 'amount', 'type']
            for fields in read_only_fields:
                kwargs[fields] = {'read_only': True}

        return kwargs

    

class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model, including user and category details, with formatted timestamps and related information.
    """
    user_email = serializers.StringRelatedField(source='user_id.email')
    category_name = serializers.StringRelatedField(source='category_id')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    user_info = UserDetailSerializer(source='user_id', read_only=True)
    category_info = CategoryDetailSerializer(source='category_id', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user_email', 'category_name', 'amount', 'type', 'source', 'description', 'user_info', 'category_info', 'created_at', 'updated_at']



class ResetPasswordRequestSerializer(serializers.Serializer):
    """
    Serializer for handling password reset requests by validating the provided email.
    """
    email = serializers.EmailField(required=True)



class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting passwords, ensuring the new password meets complexity requirements and matches the confirmation password.
    """
    new_password = serializers.RegexField(
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        write_only=True,
        error_messages={'invalid': ('Password must be at least 8 characters long with at least one capital letter and symbol')})
    confirm_password = serializers.CharField(write_only=True, required=True)