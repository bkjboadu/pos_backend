from .models import Branch
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .filters import BranchFilter
from .serializers import BranchSerializer
from audit.models import AuditLog


class BranchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        branch_filter = BranchFilter(request.GET, queryset=Branch.objects.all())
        filtered_branches = branch_filter.qs

        if not filtered_branches.exists():
            return Response({"error": "No matching branches found"}, status=404)

        # branches = Branch.objects.all()
        serializer = BranchSerializer(filtered_branches, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = request.data
        serializer = BranchSerializer(data=data)
        if serializer.is_valid():
            branch = serializer.save(created_by=request.user, updated_by=request.user)
            return Response(BranchSerializer(branch).data, status=201)
        return Response(serializer.errors, status=400)


class BranchDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        # fetch branch
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        serializer = BranchSerializer(branch)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        # fetch product to delete
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        branch.delete()
        return Response({"message": "Branch successfully deleted"}, status=200)

    def patch(self, request, pk):
        # fetch branch to update
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        data = request.data.copy()
        serializer = BranchSerializer(branch, data=data, partial=True)

        if serializer.is_valid():
            branch = serializer.save(update_by=request.user)
            return Response(BranchSerializer(branch).data, status=200)
        return Response(serializer.errors, status=400)

    def put(self, request, pk, barcode=None):
        # Fetch branch to update fully
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        data = request.data.copy()
        serializer = BranchSerializer(branch, data=data)

        if serializer.is_valid():
            branch = serializer.save(update_by=request.user)
            return Response(BranchSerializer(branch).data, status=200)
        return Response(serializer.errors, status=400)


class DeactivateBranchView(APIView):
    """
    Endpoint to deactivate a branch.
    """
    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        if not branch.is_active:
            return Response({"message":"branch is already deactivated"}, status=400)
        branch.is_active = False
        branch.updated_by = request.user
        branch.save()

        # Log to audit trail
        AuditLog.objects.create(
            action="deactivate",
            performed_by=request.user,
            resource_name="branch",
            resource_id=branch.id,
            details=f"branch {branch.id} deactivated"
        )

        return Response({"message":"branch deactivated successfully"}, status=200)

class ActivateBranchView(APIView):
    """
    Endpoint to deactivate a branch.
    """
    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        if branch.is_active:
            return Response({"message":"branch is already activated"}, status=400)
        branch.is_active = True
        branch.updated_by = request.user
        branch.save()

        # Log to audit trail
        AuditLog.objects.create(
            action="activate",
            performed_by=request.user,
            resource_name="Branch",
            resource_id=branch.id,
            details=f"branch {branch.id} deactivated"
        )

        return Response({"message":"branch activated successfully"}, status=200)
