from django.shortcuts import render
from finance.models import Transaction
from finance.serializers import CustomUserSerializer, CategorySerializer, TransactionSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated


class TransactionListCreateApiView(ListCreateAPIView):

    # permission_classes = [IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def destroy(self, destroy, *args, **kwargs):
        instance =self.get_object()
        instance.delete()
        return Response({'msg': 'soft delete performed'}, status=status.HTTP_200_OK)