from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from audit.models import AuditLog
from core.permissions import IsSuperUserOrManager

from .models import Transaction, TransactionItem
from .filters import TransactionFilter
from .serializer import TransactionSerializer, TransactionItemSerializer
from branches.models import Branch


class TransactionView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def get(self, request):
        search_query = request.query_params.get('search', '')
        branch_id = request.query_params.get('branch', None)

        if not branch_id:
            return Response({"error":"Branch ID must be provided"}, status=400)

        try:
            branch = Branch.objects.get(id=int(branch_id))
        except (ValueError, Branch.DoesNotExist):
            return Response({"error":"Invalid or non-existent branch id"}, status=400)

        # Filter permission based on user role
        if not (request.user.is_superuser or request.user.role == "admin_manager"):
            allowed_branches = (request.user.branches.values_list('id', flat=True))
            if int(branch_id) not in allowed_branches:
                return Response({"error":"You are not authorized to view transactions for this branch"}, status=403)

        queryset = Transaction.objects.filter(branch_id=branch_id)

        if search_query:
            search_filter = (
                Q(branch__id=int(search_query)) |
                Q(created_by__first_name__icontains=search_query) |
                Q(created_by__last_name__icontains=search_query) |
                Q(created_by__email__icontains=search_query) |
                Q(updated_by__first_name__icontains=search_query) |
                Q(updated_by__last_name__icontains=search_query) |
                Q(updated_by__email__icontains=search_query) |
                Q(updated_at__icontains=search_query) |
                Q(created_at__icontains=search_query) |
                Q(id__icontains=search_query) |
                Q(discount_applied__discount_type__icontains=search_query) |
                Q(discount_applied__code__icontains=search_query) |
                Q(discount_applied__value__icontains=search_query)
            )

            queryset = queryset.filter(search_filter)

        # apply filter
        filtered_sales = TransactionFilter(request.GET, queryset=queryset)
        filtered_product = filtered_sales.qs

        serializer = TransactionSerializer(filtered_product, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = request.data.copy()
        if not data.get('branch') and request.user.branches.count() == 1:
            data['branch'] = request.user.branches.first().id

        # Ensure branch is included
        branch_id = data.get('branch')
        if not branch_id:
            return Response({"error":"Branch must be specified for the transaction."}, status=400)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({"error":"Branch not found"}, status=400)

        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            transaction = serializer.save(updated_by=request.user)
            # log in audit
            AuditLog.objects.create(
                action="create",
                performed_by=request.user,
                resource_name="Transaction",
                resource_id=transaction.id,
                details=f"Transaction {transaction.id} created",
            )
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def get(self, request, pk):
        # Filter permission based on user role
        branch_id = request.query_params.get('branch', None)

        if not branch_id:
            if request.user.branches.count() == 1:
                branch_id = request.user.branches.first()
            else:
                return Response({"error":"Branch ID must be provided"}, status=400)

        try:
            branch = Branch.objects.get(id=int(branch_id))
        except (ValueError, Branch.DoesNotExist):
            return Response({"error":"Invalid or non-existent branch id"}, status=400)

        if not (request.user.is_superuser or request.user.role == "admin_manager"):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(branch_id) not in allowed_branches:
                return Response({"error":"You are not authorized to view transactions from this branch"}, status=403)

        transaction = Transaction.objects.get(id=pk)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)

        # Filter permission based on user role
        if request.user.role == 'cashier':
            return Response({"error":"You are not authorized to delete transaction"}, status=403)


        # For managers
        if not (request.user.is_superuser or request.user.role == "admin_manager"):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if transaction.branch.id not in allowed_branches:
                return Response({"error":"You are not authorized to delete transaction"}, status=403)

        transaction_id = transaction.id
        transaction.delete()

        AuditLog.objects.create(
            action="delete",
            performed_by=request.user,
            resource_name="Transaction",
            resource_id=transaction_id,
            details=f"Transaction {transaction_id} deleted",
        )

        return Response({"message": "Transaction deleted successfully"}, status=200)

    def put(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)

        # Filter permission based on user role
        if request.user.role == 'cashier':
            return Response({"error":"You are not authorized to update a transaction"}, status=403)

        if not (request.user.is_superuser or request.user.role == "admin_manager"):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(transaction.branch.id) not in allowed_branches:
                return Response({"error":"You are not authorized to updated this transaction."}, status=403)

        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            # Log changes for audit
            changes = []
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(transaction, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            serializer.save(updated_by=request.user)

            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="Transaction",
                resource_id=transaction.id,
                details=f"Transaction {transaction.id} updated",
            )

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)

        # Filter permission based on user role
        if request.user.role == 'cashier':
            return Response({"error":"You are not authorized to update a transaction"}, status=403)

        if not (request.user.is_superuser or request.user.role == "admin_manager"):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(transaction.branch.id) not in allowed_branches:
                return Response({"error":"You are not authorized to updated this transaction."}, status=403)

        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            # Log changes for audit
            changes = []
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(transaction, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            serializer.save(updated_by=request.user)

            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="Transaction",
                resource_id=transaction.id,
                details=f"Transaction {transaction.id} updated",
            )

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class TransactionItemView(APIView):
    def get(self, request):
        branch_id = request.query_params.get('branch', '')

        if not branch_id and request.user.branches.count() == 1:
            branch_id = request.user.branches.first()

        if not branch_id:
            return Response({"error":"branch id must be provided"}, status=400)

        # check if branch exist
        try:
            branch = Branch.objects.get(id=branch_id)
        except (ValueError, Branch.DoesNotExist):
            return Response({"error": 'Invalid branch id or non-existent branch'}, status=400)

        if not (request.user.is_superuser or request.user.role == "admin_manager"):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(branch_id) not in allowed_branches:
                return Response({"error":"You are not authorized to updated this transaction."}, status=403)

        # Filter out permission based on user role
        transaction_items = TransactionItem.objects.filter(transaction__branch__id=branch_id)

        serializer = TransactionItemSerializer(transaction_items, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = TransactionItemSerializer(data=request.data)
        if serializer.is_valid():
            transactionitem_instance = serializer.save()

            # log in audit
            AuditLog.objects.create(
                action="create",
                performed_by=request.user,
                resource_name="TransactionItems",
                resource_id=transactionitem_instance.id,
                details=f"Customer {transactionitem_instance.id} created",
            )

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class TransactionItemDetailView(APIView):
    def get(self, request, pk):
        try:
            transaction_item = get_object_or_404(TransactionItem, id=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

        if not(request.user.is_superuser or request.user.role == 'admin_manager'):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(transaction_item.transaction.branch.id) not in allowed_branches:
                return Response({"error":"You do not have permission to this transaction"}, status=403)

        serializer = TransactionItemSerializer(transaction_item)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        try:
            transaction_item = get_object_or_404(TransactionItem, id=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

        if request.user.role == 'cashier':
            return Response({"error":"You do not have permission to delete this transaction"}, status=403)

        if not(request.user.is_superuser or request.user.role == 'admin_manager'):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(transaction_item.transaction.branch.id) not in allowed_branches:
                return Response({"error":"You do not have permission to this transaction"}, status=403)

        transactionitem_instance = transaction_item.id
        transaction_item.delete()

        # log in audit
        AuditLog.objects.create(
            action="delete",
            performed_by=request.user,
            resource_name="TransactionItems",
            resource_id=transactionitem_instance,
            details=f"Customer {transactionitem_instance} deleted",
        )

        return Response(
            {"message": "Transaction Item deleted successfully"}, status=200
        )

    def put(self, request, pk):
        try:
            transaction_item = get_object_or_404(TransactionItem, id=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

        if request.user.role == 'cashier':
            return Response({"error":"You do not have permission to delete this transaction"}, status=403)

        if not(request.user.is_superuser or request.user.role == 'admin_manager'):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(transaction_item.transaction.branch.id) not in allowed_branches:
                return Response({"error":"You do not have permission to this transaction"}, status=403)

        serializer = TransactionItemSerializer(transaction_item, data=request.data)
        if serializer.is_valid():
            # Log changes for audit
            changes = []
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(transaction_item, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            serializer.save()

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="TransactionItem",
                resource_id=transaction_item.id,
                details=details,
            )

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        try:
            transaction_item = get_object_or_404(TransactionItem, id=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

        if request.user.role == 'cashier':
            return Response({"error":"You do not have permission to delete this transaction"}, status=403)

        if not(request.user.is_superuser or request.user.role == 'admin_manager'):
            allowed_branches = request.user.branches.values_list('id', flat=True)
            if int(transaction_item.transaction.branch.id) not in allowed_branches:
                return Response({"error":"You do not have permission to this transaction"}, status=403)

        serializer = TransactionItemSerializer(
            transaction_item, data=request.data, partial=True
        )
        if serializer.is_valid():
            # Log changes for audit
            changes = []
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(transaction_item, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            serializer.save()

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="TransactionItem",
                resource_id=transaction_item.id,
                details=details,
            )

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
