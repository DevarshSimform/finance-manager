import redis,time

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group
from finance.models import Transaction, Category
from finance.serializers import CategorySerializer, TransactionSerializer
from finance.signals import post_save_with_request
from finance.custompermissions import IsAuthenticatedAndOwner 

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from guardian.shortcuts import assign_perm, get_objects_for_user, ObjectPermissionChecker



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

    permission_classes = [IsAuthenticatedAndOwner]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            category = Category.objects.get(id=request.data.get('id'))
            group = Group.objects.get(name='default_categories')
            checker = ObjectPermissionChecker(group)
            serializer = CategorySerializer(instance=category, data=request.data, partial=partial)
            if serializer.is_valid():
                if request.user.has_perm('finance.view_category', category) and not checker.has_perm('view_category', category):
                    serializer.save()
                    return Response({'message': 'Category Updated'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'You cannot update this category'}, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Category or Group does not exists'}, status=status.HTTP_404_NOT_FOUND)


    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        print(request.data)
        try:
            category = Category.objects.get(id=request.data.get('id'))
            group = Group.objects.get(name='default_categories')
            checker = ObjectPermissionChecker(group)
            if request.user.has_perm('finance.view_category', category) and not checker.has_perm('view_category', category):
                category.delete()
                return Response({'message': 'Category deleted'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You cannot delete this category'}, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({'message': 'Category or Group does not exists'}, status=status.HTTP_404_NOT_FOUND)



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
    
