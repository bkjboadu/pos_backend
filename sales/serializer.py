from rest_framework.serializers import ModelSerializer
from .models import Transaction, TransactionItem


class TransactionSerializer(ModelSerializer):
    class Meta:
        models = Transaction
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")


class TransactionItemSerializer(ModelSerializer):
    class Meta:
        models = TransactionItem
        fields = "__all__"