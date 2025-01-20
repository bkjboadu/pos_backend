from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Transaction, TransactionItem
from .serializer import TransactionSerializer, TransactionItemSerializer
from audit.models import AuditLog


class TransactionView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
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
    def get(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
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
        transaction_items = TransactionItem.objects.all()
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
        transaction_item = TransactionItem.objects.get(pk=pk)
        serializer = TransactionItemSerializer(transaction_item)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        transaction_item = TransactionItem.objects.get(pk=pk)
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
        transaction_item = TransactionItem.objects.get(pk=pk)
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
        transaction_item = TransactionItem.objects.get(pk=pk)
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
