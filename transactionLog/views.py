from django.shortcuts import render

from rest_framework.generics import ListAPIView
from transactionLog.models import TransactionLog
from transactionLog.serializers import TransactionLogSerializer


class TransactionLogListAPIView(ListAPIView):

    queryset = TransactionLog.objects.order_by('-logged_at')
    serializer_class = TransactionLogSerializer
