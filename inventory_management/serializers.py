from rest_framework.serializers import ModelSerializer
from .models import Product, StockInput


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "image",
            "barcode",
            "price",
            "stock",
            "sku",
            "created_at",
            "updated_at",
        ]
        read_only_field = (
            "created_at",
            "updated_at",
        )


class StockInputSerializer(ModelSerializer):
    class Meta:
        model = StockInput
        fields = "__all__"
        read_only_fields = ("added_by", "date_added")
