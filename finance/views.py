import redis,time

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group
from finance.models import Transaction, Category
from finance.serializers import CategorySerializer, TransactionSerializer, TransactionDetailSerializer
from finance.signals import post_save_with_request
from finance.custompermissions import HasObjectPermOrAdmin, IsOwnerOrAdmin

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from guardian.shortcuts import assign_perm, get_objects_for_user, ObjectPermissionChecker



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

from rest_framework.throttling import ScopedRateThrottle

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

    def perform_destroy(self, serializer):
        raise PermissionDenied(detail='You cannot delete any transaction')
    
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
    
