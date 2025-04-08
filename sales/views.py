from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from audit.models import AuditLog
from core.permissions import IsSuperUserOrManager

from .models import Transaction, TransactionItem
from .filters import TransactionFilter
from .serializer import TransactionSerializer, TransactionItemSerializer


class TransactionView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def get(self, request):
        search_query = request.query_params.get('search', '')

        # Superuser can view all transactions
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                queryset = Transaction.objects.filter(created_by=request.user)
            else:
                queryset = Transaction.objects.all()
        except Exception as e:
            return Response({"error": e}, status=400)

        if search_query:
            search_filter = (
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
        serializer = TransactionSerializer(data=request.data)
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
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction = Transaction.objects.get(pk=pk, created_by=request.user)
            else:
                transaction = Transaction.objects.get(pk=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction = Transaction.objects.get(pk=pk, created_by=request.user)
            else:
                transaction = Transaction.objects.get(pk=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

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
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction = Transaction.objects.get(pk=pk, created_by=request.user)
            else:
                transaction = Transaction.objects.get(pk=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

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
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction = Transaction.objects.get(pk=pk, created_by=request.user)
            else:
                transaction = Transaction.objects.get(pk=pk)
        except Exception as e:
            return Response({"error": e}, status=400)

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
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction_items = TransactionItem.objects.filter(transaction__created_by=request.user)
            else:
                transaction_items = TransactionItem.objects.all()
        except Exception as e:
            return Response({"error": e}, status=400)


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
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction_item = TransactionItem.objects.filter(transaction__created_by=request.user)
            else:
                transaction_item = TransactionItem.objects.all()
        except Exception as e:
            return Response({"error": e}, status=400)

        serializer = TransactionItemSerializer(transaction_item)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        try:
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction_item = TransactionItem.objects.filter(transaction__created_by=request.user)
            else:
                transaction_item = TransactionItem.objects.all()
        except Exception as e:
            return Response({"error": e}, status=400)

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
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction_item = TransactionItem.objects.filter(transaction__created_by=request.user)
            else:
                transaction_item = TransactionItem.objects.all()
        except Exception as e:
            return Response({"error": e}, status=400)

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
            if not (request.user.is_superuser or request.user.role == "manager"):
                transaction_item = TransactionItem.objects.filter(transaction__created_by=request.user)
            else:
                transaction_item = TransactionItem.objects.all()
        except Exception as e:
            return Response({"error": e}, status=400)

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
