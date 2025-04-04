import redis,time

from django.shortcuts import render, get_object_or_404
from finance.models import Transaction
from finance.serializers import RegisterSerializer, LoginSerializer, CategorySerializer, TransactionSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken




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
    


class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'User Registered'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'msg': 'Enter valid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Refresh token blacklisted and user logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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