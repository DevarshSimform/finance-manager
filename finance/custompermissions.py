from rest_framework.permissions import BasePermission
from guardian.core import ObjectPermissionChecker
from django.contrib.auth.models import Group
from guardian.shortcuts import get_objects_for_user


class HasObjectPermOrAdmin(BasePermission):
    """
    Allows access only to users which has object-level permission or superuser.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return request.user.has_perm('finance.view_category', obj) or request.user.is_superuser
        else:
            group = Group.objects.get(name='default_categories')
            checker = ObjectPermissionChecker(group)
            if request.user.has_perm('finance.view_category', obj) and not checker.has_perm('view_category', obj):
                return True
            else:
                if request.user.is_superuser:
                    return True
                return False
    

class IsOwnerOrAdmin(BasePermission):
    '''
    Allow access to only transaction which is created by user
    '''

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user or request.user.is_superuser