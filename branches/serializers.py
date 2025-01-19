from .models import Branch
from rest_framework.serializers import ModelSerializer

class BranchSerializer(ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "created_at"
        )
