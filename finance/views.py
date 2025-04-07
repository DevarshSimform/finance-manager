import redis,time

from django.shortcuts import render, get_object_or_404
from finance.models import Transaction, Category
from finance.serializers import CategorySerializer, TransactionSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView







class TransactionListCreateAPIView(ListCreateAPIView):

    # permission_classes = [IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def destroy(self, destroy, *args, **kwargs):
        instance =self.get_object()
        instance.delete()
        return Response({'msg': 'soft delete performed'}, status=status.HTTP_200_OK)
    


class BalanceViewAPIView(APIView):
    ''' Login Required, To retrieve logged in users balance '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ''' return user's balance by calculating it using property function named balance '''
        balance = request.user.balance
        return Response({'total-balance': balance} ,status=status.HTTP_200_OK)
    
