from rest_framework import serializers

from transactionLog.models import TransactionLog


class TransactionLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = '__all__'