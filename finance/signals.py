from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from finance.models import CustomUser
from django.dispatch import receiver, Signal
from guardian.shortcuts import assign_perm


post_save_with_request = Signal()


@receiver(post_save, sender=CustomUser)
def default_user_categories(sender, instance, created, **kwargs):
    """
    Assigns the 'default_categories' group to a newly created user upon creation.
    """
    if created:
        user = instance
        default_group, _ = Group.objects.get_or_create(name='default_categories')
        user.groups.add(default_group)


@receiver(post_save_with_request)
def category_owner_permission(sender, instance, request, created, is_superuser, **kwargs):
    """
    Handles permission assignment for category owners and superusers upon category creation.
    """
    if created:
        category = instance
        user = request.user
        assign_perm('view_category', user, category)
        if is_superuser:
            group = Group.objects.get_or_create(name='default_categories')
            assign_perm('view_category', group, category)