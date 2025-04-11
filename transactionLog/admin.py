from django.contrib import admin

from transactionLog.models import TransactionLog

@admin.register(TransactionLog)
class CategoryAdmin(admin.ModelAdmin):
    model = TransactionLog
    list_display = ['id', 'transaction', 'user', 'category', 'amount', 'type', 'action', 'description', 'logged_at']