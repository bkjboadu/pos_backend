from rest_framework.serializers import ModelSerializer
from .models import Company, Branch


class BranchSerializer(ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "company",
            "address",
            "created_at",
        ]
        read_only_fields = ("created_at",)


class CompanySerializer(ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "country", "address", "created_at", "branches"]
        read_only_fields = ("created_at",)
