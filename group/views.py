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



class GroupListCreateAPIView(ListCreateAPIView):

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    # serializer_class = GroupSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupCreateSerializer
        else:
            return GroupListSerializer


class GroupRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer



class AddMemberToGroup(CreateAPIView):

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AddMemberToGroupSerializer


class RemoveMemberFromGroup(CreateAPIView):

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RemoveMemberFromGroupSerializer


class ExpenseListCreateAPIView(ListCreateAPIView):

    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            SerializerCreateClass = ExpenseCreateSerializerFactory.get_serializer(self.request.data)
            return SerializerCreateClass
        else:
            return ExpenseListSerializer


class ExpenseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer


class SettleUpExpenseAPIView(CreateAPIView):

    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SettleUpExpenseSerializer


class RevertSettleUpAPIView(CreateAPIView):

    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RevertSettleUpSerializer