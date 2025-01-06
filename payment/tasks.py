import requests, os
from celery import shared_task
from inventory_management.models import Transaction,TransactionItem
from django.db import transaction

@shared_task
def process_order(transaction_id):
    try:
        transaction_instance = Transaction.objects.get(id=transaction_id)

        # Update a stock and save order item in a transaction
        with transaction.atomic():
            for item in transaction_instance.items.all():
                product = item.product

                if product.quantity_in_stock < item.quantity:
                    return {
                        "status": "failed",
                        "message": f"Insufficient stock for {product.name}",
                    }

                product.stock -= item.quantity
                product.save()

        return {
            "message":"Payment Complete"
        }
    except Transaction.DoesNotExist:
        return {"status": "failed", "message": "Order not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
