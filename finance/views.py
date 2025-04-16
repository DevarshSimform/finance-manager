from django.db import connection
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from finance.models import Transaction, Category, CustomUser, PasswordReset
from finance.serializers import (
    CategorySerializer, 
    TransactionSerializer, 
    TransactionDetailSerializer, 
    UserDetailSerializer, 
    ResetPasswordRequestSerializer,
    ResetPasswordSerializer
)
from finance.signals import post_save_with_request
from finance.custompermissions import HasObjectPermOrAdmin, IsOwnerOrAdmin

from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView, 
    ListCreateAPIView, 
    RetrieveAPIView, 
    GenericAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import ScopedRateThrottle

from guardian.shortcuts import get_objects_for_user



class UserProfileView(RetrieveAPIView):
    """
    View to retrieve the authenticated user's profile details.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user    



class CategoryListCreateAPIView(ListCreateAPIView):
    """
    API view for listing and creating categories with custom permissions, throttling, filtering, and signals.
    """
    
    permission_classes = [HasObjectPermOrAdmin]
    serializer_class = CategorySerializer
    throttle_classes = [ScopedRateThrottle]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        return get_objects_for_user(self.request.user, 'view_category', Category)
    
    def post(self, request):
        ''' sending request in custom signal to get user and add object permission to created category '''
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            name = serializer.validated_data.get('name')
            category = Category.objects.get(name=name)
            post_save_with_request.send(sender=Category, instance=category, request=request, created=True, is_superuser=request.user.is_superuser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_throttles(self):
        if self.request.method == 'GET':
            self.throttle_scope = 'high'
        else:
            self.throttle_Scope = 'low'
        return super(CategoryListCreateAPIView, self).get_throttles()

        

class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a Category instance with specific permissions.
    """

    permission_classes = [HasObjectPermOrAdmin]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class TransactionListCreateAPIView(ListCreateAPIView):
    """
    API view for listing and creating transactions with permissions, throttling, filtering, and superuser restrictions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    throttle_classes = [ScopedRateThrottle]
    filter_backends = [SearchFilter]
    search_fields = ['description', 'amount', 'type', 'source']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transaction.objects.all()
        return Transaction.objects.filter(user_id=self.request.user)
    
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            raise PermissionDenied(detail='Superuser cannot create any transaction')
        return super().perform_create(serializer)
    
    def get_throttles(self):
        if self.request.method == 'GET':
            self.throttle_scope = 'high'
        else:
            self.throttle_Scope = 'low'
        return super(TransactionListCreateAPIView, self).get_throttles()
        


class TransactionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a Transaction instance with custom permissions, throttling, and serializers.
    """
    
    permission_classes = [IsOwnerOrAdmin]
    throttle_classes = [ScopedRateThrottle]

    queryset = Transaction.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TransactionDetailSerializer
        return TransactionSerializer

    # def perform_destroy(self, serializer):
    #     raise PermissionDenied(detail='You cannot delete any transaction')
    
    def get_throttles(self):
        if self.request.method.lower() == 'get':
            self.throttle_scope = 'high'
        else:
            self.throttle_scope = 'low'
        return super(TransactionRetrieveUpdateDestroyAPIView, self).get_throttles()
    


class BalanceViewAPIView(APIView):
    """
    APIView to retrieve the authenticated user's total balance using the balance property.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the user's balance by calculating it using the property function named balance."""
        balance = request.user.balance
        return Response({'total-balance': balance}, status=status.HTTP_200_OK)
    


class RequestPasswordReset(GenericAPIView):
    """
    Handles password reset requests by generating a token, saving it, and sending a reset email to the user.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_Scope = 'low'
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        to_email = request.data['email']
        user = CustomUser.objects.filter(email__iexact=to_email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=to_email, token=token)
            reset.save()

            reset_url = f"http://localhost:8000/api/v1/reset-password/{token}"

            email = EmailMessage(
                subject="Reset Password",
                body=reset_url,
                from_email=settings.EMAIL_HOST_USER,
                to=[to_email],
            )
            email.send()

            return Response({'success': 'Check your email to reset password'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with credentials not found"}, status=status.HTTP_404_NOT_FOUND)
        


class ResetPassword(GenericAPIView):
    """
    Handles password reset by validating the token, updating the user's password, and deleting the reset token.
    """
    
    permission_classes = []
    serializer_class = ResetPasswordSerializer

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        new_password = data['new_password']
        confirm_password = data['confirm_password']

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        reset_obj = PasswordReset.objects.filter(token=token).first()

        if not reset_obj:
            return Response({'error': 'Invalid token error'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(request.data['new_password'])
            user.save()
            reset_obj.delete()
            return Response({'success': 'Password updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No user found'}, status=status.HTTP_404_NOT_FOUND)


class GetCategoryTotal(APIView):
    """
    APIView to retrieve total amounts grouped by category for the authenticated user.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_total_by_category(%s)", [user_id])
                data = cursor.fetchall()

            result = [{'category': row[0], 'total_amount': float(row[1])} for row in data]
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TransactionDetailByDate(APIView):
    """
    Handles GET requests to retrieve transaction details by date for the authenticated user.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_transaction_details_by_date(%s)", [user_id])
                columns = [col[0] for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)