from rest_framework.serializers import ModelSerializer
from .models import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "barcode",
            "price",
            "stock",
            "created_at",
            "updated_at",
        ]
        read_only_field = (
            "created_at",
            "updated_at",
        )
