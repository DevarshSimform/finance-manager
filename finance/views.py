from django.shortcuts import render
from finance.models import Transaction
from finance.serializers import CustomUserSerializer, CategorySerializer, TransactionSerializer

from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated


class TransactionListApiView(ListCreateAPIView):

    # Implement custom model manager first
    permission_classes = [IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer