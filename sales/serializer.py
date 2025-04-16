from rest_framework.serializers import ModelSerializer
from .models import Transaction, TransactionItem
from customers.serializers import CustomerSerializer


class TransactionSerializer(ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")


class TransactionItemSerializer(ModelSerializer):
    class Meta:
        model = TransactionItem
        fields = "__all__"
