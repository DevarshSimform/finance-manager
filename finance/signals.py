from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from finance.models import CustomUser, Category
from django.dispatch import receiver, Signal
from guardian.shortcuts import assign_perm


post_save_with_request = Signal()


@receiver(post_save, sender=CustomUser)
def default_user_categories(sender, instance, created, **kwargs):
    if created:
        user = instance
        default_group = Group.objects.get(name='default_categories')
        user.groups.add(default_group)


@receiver(post_save_with_request)
def category_owner_permission(sender, instance, request, created, is_superuser, **kwargs):
    if created:
        category = instance
        user = request.user
        assign_perm('view_category', user, category)
        if is_superuser:
            group = Group.objects.get(name='default_categories')
            assign_perm('view_category', group, category)
    
    #If super_user create category then that will be accessible by all users.



# @receiver(post_save, sender=Category)
# def category_owner_permission(sender, instance, request ,created, **kwargs):
#     if created:
#         category = instance
#         user = request.user
#         assign_perm('view_category', user, category)