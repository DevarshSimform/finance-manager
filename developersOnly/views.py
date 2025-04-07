from django.shortcuts import get_object_or_404
from finance.models import Transaction, CustomUser
from finance.serializers import TransactionSerializer
from finance.serializers import RegisterSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


# ------------ Transaction ---------------

class AllTransactionAPIView(APIView):
    '''To retrieve all transactions including soft-deleted '''
    def get(self, request):
        transactions = Transaction.objects.with_deleted()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DeletedTransactionAPIView(APIView):
    ''' To retrieve soft-deleted transactions '''
    def get(self, request):
        transactions = Transaction.objects.only_deleted()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RestoreTransactionAPIView(APIView):
    ''' To restore soft-deleted transaction '''
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction.objects.only_deleted(), pk=pk)
        if not transaction.is_deleted:
            return Response({'message': 'Transaction is active'}, status=status.HTTP_400_BAD_REQUEST)
        transaction.restore()
        return Response({'message': 'Transaction Restored'}, status=status.HTTP_200_OK)
    

class HardDeleteTransactionAPIView(APIView):
    ''' To delete transaction permanently (hard-delete) '''
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction.objects.with_deleted(), pk=pk)
        if not transaction: 
            return Response({'message': 'Transaction doesnot exists'}, status=status.HTTP_400_BAD_REQUEST)
        transaction.delete(hard=True)
        return Response({'message': 'Transaction Hard deleted'}, status=status.HTTP_200_OK)
    


# ------------ User ---------------

class AllUserAPIView(APIView):
    ''' To retrieve all users including soft-deleted '''
    def get(self, request):
        users = CustomUser.objects.with_deleted()
        serializer = RegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DeletedUserAPIView(APIView):
    ''' To retrieve soft-deleted users '''
    def get(self, request):
        users = CustomUser.objects.only_deleted()
        serializer = RegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RestoreUserAPIView(APIView):
    ''' To restore soft-deleted user '''
    def post(self, request, pk):
        user = get_object_or_404(CustomUser.objects.only_deleted(), pk=pk)
        if not user.is_deleted:
            return Response({'message': 'User is Active'}, status=status.HTTP_400_BAD_REQUEST)
        user.restore()
        return Response({'message': 'User restored'}, status=status.HTTP_200_OK)
    

class HardDeleteUserAPIView(APIView):
    ''' To delete user permanently user (hard-delete) '''
    def post(self, request, pk):
        user = get_object_or_404(CustomUser.objects.with_deleted, pk=pk)
        if not user:
            return Response({'message': 'User doesnot exists'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete(hard=True)
        return Response({'message': 'User hard deleted'}, status=status.HTTP_200_OK)