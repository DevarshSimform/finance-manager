from django.contrib import admin
from group.models import Group, GroupMember, Expense, SplitExpense


class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1
    readonly_fields = ('joined_at',)  # show joined_at as read-only
    fields = ('user', 'joined_at')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'created_at')
    inlines = [GroupMemberInline]


class SplitExpenseInline(admin.TabularInline):
    model = SplitExpense
    extra = 1
    fields = ('user', 'amount', 'is_settled')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'created_by', 'description', 'amount', 'created_at')
    inlines = [SplitExpenseInline]
