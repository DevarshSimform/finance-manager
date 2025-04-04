import redis,time

from django.shortcuts import render, get_object_or_404
from finance.models import Transaction
from finance.serializers import RegisterSerializer, LoginSerializer, CategorySerializer, TransactionSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView





class TransactionListCreateApiView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def destroy(self, destroy, *args, **kwargs):
        instance =self.get_object()
        instance.delete()
        return Response({'msg': 'soft delete performed'}, status=status.HTTP_200_OK)
    







class BalanceViewAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        balance = request.user.balance
        return Response({'total-balance': balance} ,status=status.HTTP_200_OK)
    

class AllTransactionAPIView(APIView):
    
    def get(self, request):
        transactions = Transaction.objects.with_deleted()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DeletedTransactionAPIView(APIView):

    def get(self, request):
        transactions = Transaction.objects.only_deleted()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RestoreTransactionAPIView(APIView):

    def post(self, request, pk):
        transaction = get_object_or_404(Transaction.objects.only_deleted(), pk=pk)
        if not transaction.is_deleted:
            return Response({'msg': 'transaction is active'}, status=status.HTTP_400_BAD_REQUEST)
        transaction.restore()
        return Response({'msg': 'Transaction Restored'}, status=status.HTTP_200_OK)


class HardDeleteTransactionAPIView(APIView):

    def delete(self, request, pk):
        transaction = get_object_or_404(Transaction.objects.with_deleted(), pk=pk)
        transaction.delete(hard=True)
        return Response({'msg': 'Transaction Hard deleted'}, status=status.HTTP_200_OK)