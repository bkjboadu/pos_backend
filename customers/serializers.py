from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "name",
            "email",
            "phone_number",
            "address",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_field = (
            "created_by",
            "created_at",
            "updated_at",
        )

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
