from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from group.models import (
    Group, Expense
)
from group.serializers import GroupSerializer, GroupListSerializer, GroupCreateSerializer, ExpenseSerializer, ExpenseListSerializer, ExpenseCreateSerializerFactory, AddMemberToGroupSerializer, RemoveMemberFromGroupSerializer, SettleUpExpenseSerializer, RevertSettleUpSerializer
from django.db.models import Q


class GroupListCreateAPIView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    # serializer_class = GroupSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Group.objects.all()
        return Group.objects.filter(members__in=[self.request.user])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupCreateSerializer
        else:
            return GroupListSerializer


class GroupRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Group.objects.all()
        return Group.objects.filter(members__in=[self.request.user])


class AddMemberToGroup(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AddMemberToGroupSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Group.objects.all()
        return Group.objects.filter(members__in=[self.request.user])


class RemoveMemberFromGroup(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = RemoveMemberFromGroupSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Group.objects.all()
        return Group.objects.filter(members__in=[self.request.user])

class ExpenseListCreateAPIView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        return Expense.objects.filter(
            Q(created_by=self.request.user) | Q(split_between__in=[self.request.user])
        ).distinct()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            SerializerCreateClass = ExpenseCreateSerializerFactory.get_serializer(self.request.data)
            return SerializerCreateClass
        else:
            return ExpenseListSerializer


class ExpenseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        return Expense.objects.filter(
            Q(created_by=self.request.user) | Q(split_between__in=[self.request.user])
        ).distinct()


class SettleUpExpenseAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = SettleUpExpenseSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        return Expense.objects.filter(
            Q(created_by=self.request.user) | Q(split_between__in=[self.request.user])
        ).distinct()


class RevertSettleUpAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = RevertSettleUpSerializer

    def get_queryset(self):
        if self.request.user.is_suppersuer:
            return Expense.objects.all()
        return Expense.objects.filter(
            Q(created_by=self.request.user) | Q(split_between__in=[self.request.user])
        ).distinct()
