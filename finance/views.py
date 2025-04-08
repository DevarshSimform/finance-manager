import redis,time

from django.shortcuts import render, get_object_or_404
from finance.models import Transaction, Category
from finance.serializers import CategorySerializer, TransactionSerializer
from finance.signals import post_save_with_request
from finance.custompermissions import IsAuthenticatedAndOwner 

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from guardian.shortcuts import get_objects_for_user



class CategoryListAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticatedAndOwner]
    serializer_class = CategorySerializer
    # queryset = Category.objects.all()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        return get_objects_for_user(self.request.user, 'view_category', Category)

class CategoryCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    permission_classes = [IsAdminUser]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class TransactionListCreateAPIView(ListCreateAPIView):

    # permission_classes = [IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def destroy(self, destroy, *args, **kwargs):
        return Response({'message': 'You cannot delete any transaction'}, status=status.HTTP_403_FORBIDDEN)
    


class BalanceViewAPIView(APIView):
    ''' Login Required, To retrieve logged in users balance '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ''' return user's balance by calculating it using property function named balance '''
        balance = request.user.balance
        return Response({'total-balance': balance} ,status=status.HTTP_200_OK)
    

from django.contrib.auth.models import Group


# class group_adding(APIView):

#     def get(self, reqeust):
#         group, created = Group.objects.get_or_create(name='default_categories')

#         categories = Category.objects.all()
#         for category in categories:
#             category.group.add(category)

#         print(group)
#         return Response({'GroupName': 'Done'}, status=status.HTTP_200_OK)
