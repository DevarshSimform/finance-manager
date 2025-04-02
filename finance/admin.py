from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from finance.models import CustomUser, Category, Transaction


# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'username', 'email', 'balance', 'date_joined')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'email', 'balance', 'date_joined')
    # fieldsets = UserAdmin.fieldsets + (
        
    #     ("Custom Fields", {"fields": ("balance",)}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     ("Custom Fields", {"fields": ("balance",)}),
    # )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ("Custom Fields", {"fields": ("balance",)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'balance', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('email', 'username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ['id', 'name', 'type']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ['id', 'user_id', 'category_id', 'amount', 'description']