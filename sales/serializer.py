from rest_framework.serializers import ModelSerializer, CharField, DecimalField
from .models import Transaction, TransactionItem
from customers.serializers import CustomerSerializer


class TransactionSerializer(ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")


class TransactionItemSerializer(ModelSerializer):
    product_name = CharField(source="product.name", read_only=True)
    product_price = DecimalField(source="product.price", read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = TransactionItem
        fields = [
            "id",
            "transaction",
            "product",
            "quantity",
            "total_amount",
            "product_name",
            "product_price",
        ]
