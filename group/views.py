from django.shortcuts import render

from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from group.models import (
    Group,
)
from group.serializers import GroupSerializer, GroupCreateSerializer


class GroupListCreateAPIView(ListCreateAPIView):

    queryset = Group.objects.all()
    permission_classes = [AllowAny]
    # serializer_class = GroupSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupCreateSerializer
        else:
            return GroupSerializer