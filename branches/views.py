from core.permissions import IsSuperUserOrManager
from .models import Branch
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .filters import BranchFilter
from .serializers import BranchSerializer
from audit.models import AuditLog


class BranchView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def get(self, request):
        search_query = request.GET.get('search', "")

        if request.user.role != "admin_manager":
            user_branches = request.user.branches.values_list('id', flat=True)
            base_queryset = Branch.objects.filter(id__in=user_branches)
        else:
            base_queryset = Branch.objects.all()

        branch_filter = BranchFilter(request.GET, queryset=base_queryset)
        filtered_branches = branch_filter.qs

        if search_query:
            try:
                search_id = int(search_query)
                id_filter = Q(id=search_id)
            except ValueError:
                id_filter = Q()

            search_filters = (
                id_filter |
                Q(name__icontains=search_query) |
                Q(created_at__icontains=search_query) |
                Q(updated_at__icontains=search_query) |
                Q(address__icontains=search_query)
            )
            filtered_branches = filtered_branches.filter(search_filters)

        if not filtered_branches.exists():
            return Response({"errror": "No matching branches found"}, status=404)

        serializer = BranchSerializer(filtered_branches, many=True)
        return Response(serializer.data, status=200)


    def post(self, request):
        if request.user.role != 'admin_manager':
            return Response({"error":"You do have permission to create a branch here"})

        data = request.data
        serializer = BranchSerializer(data=data)
        if serializer.is_valid():
            branch = serializer.save(created_by=request.user, updated_by=request.user)
            return Response(BranchSerializer(branch).data, status=201)
        return Response(serializer.errors, status=400)


class BranchDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def get(self, request, pk=None):
        # check if user have permission to the branch
        if not (request.user.is_superuser or request.user.role == 'admin_manager'):
            if pk not in request.user.branches.value_lists('id', flat=True):
                return Response({"error":"You do not have permission to this branch"}, status=400)

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
        # check if user have permission to the branch
        if not (request.user.is_superuser or request.user.role == 'admin_manager'):
            if pk not in request.user.branches.value_list('id', flat=True):
                return Response({"error":"You do not have permission to this branch"}, status=400)

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
        # check if user have permission to the branch
        if not (request.user.is_superuser or request.user.role == 'admin_manager'):
            if pk not in request.user.branches.value_list('id', flat=True):
                return Response({"error":"You do not have permission to this branch"}, status=400)

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
        # check if user have permission to the branch
        if not (request.user.is_superuser or request.user.role == 'admin_manager'):
            if pk not in request.user.branches.value_list('id', flat=True):
                return Response({"error":"You do not have permission to this branch"}, status=400)

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
