import redis,time

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group
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

from guardian.shortcuts import assign_perm, get_objects_for_user, ObjectPermissionChecker


class UserProfileView(RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user    



class CategoryListCreateAPIView(ListCreateAPIView):
    
    permission_classes = [HasObjectPermOrAdmin]
    serializer_class = CategorySerializer
    # queryset = Category.objects.all()

    def get_queryset(self):
        ''' It will return queryset of category objects which is accessible by request.user '''
        if self.request.user.is_superuser:
            return Category.objects.all()
        return get_objects_for_user(self.request.user, 'view_category', Category)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            name = serializer.validated_data.get('name')
            category = Category.objects.get(name=name)
            post_save_with_request.send(sender=Category, instance=category, request=request, created=True, is_superuser=request.user.is_superuser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    permission_classes = [HasObjectPermOrAdmin]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class TransactionListCreateAPIView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]

    # queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transaction.objects.all()
        return Transaction.objects.filter(user_id=self.request.user)
    
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            raise PermissionDenied(detail='Superuser cannot create any transaction')
        return super().perform_create(serializer)
    
    def get_throttles(self):
        if self.request.method.lower() == 'get':
            self.throttle_scope = 'high'
        else:
            self.throttle_Scope = 'low'
        return super(TransactionListCreateAPIView, self).get_throttles()
        


class TransactionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    '''' Deletion of transaction is disabled and description can only be updated '''

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
    ''' Login Required, To retrieve logged in users balance '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ''' return user's balance by calculating it using property function named balance '''
        balance = request.user.balance
        return Response({'total-balance': balance} ,status=status.HTTP_200_OK)
    


class RequestPasswordReset(GenericAPIView):

    permission_classes = [AllowAny]
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
                subject="Verify Your Email",
                body=reset_url,
                from_email=settings.EMAIL_HOST_USER,
                to=[to_email],
            )
            # email.content_subtype = "html"
            email.send()

            return Response({'success': 'Check your email to reset password'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with credentials not found"}, status=status.HTTP_404_NOT_FOUND)
        


class ResetPassowrd(GenericAPIView):
    
    permission_classes = []
    serializer_class = ResetPasswordSerializer

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        new_passowrd = data['new_password']
        confirm_password = data['confirm_password']

        if new_passowrd != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        reset_obj = PasswordReset.objects.filter(token=token).first()

        if not reset_obj:
            return Response({'error':'Invalid token error'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(request.data['new_password'])
            user.save()
            print(f'deleting - {reset_obj}')
            reset_obj.delete()
            return Response({'success':'Password updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No user found'}, status=status.HTTP_404_NOT_FOUND)
