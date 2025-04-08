from rest_framework.permissions import BasePermission
from guardian.core import ObjectPermissionChecker
from django.contrib.auth.models import Group
from guardian.shortcuts import get_objects_for_user


class IsAuthenticatedAndOwner(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return bool(request.user and request.user.is_authenticated)