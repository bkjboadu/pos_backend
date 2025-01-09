from payment.models import Payment
from inventory_management.models import Product
from sales.models import Transaction, TransactionItem
from discounts.models import Promotion, Discount
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response

def create_transaction(items, total_amount=None):
    # create transaction
    try:
        with transaction.atomic():
            if total_amount is not None:
                transaction_instance = Transaction.objects.create(total_amount=total_amount)
            else:
                transaction_instance = Transaction.objects.create()

            for item in items:
                # get product instance
                product = get_object_or_404(Product, id=item["product"])
                TransactionItem.objects.create(
                    transaction=transaction_instance,
                    product=product,
                    quantity=item["quantity"],
                    total_amount=item["quantity"] * product.price,
                )
            transaction_instance.save()
        return transaction_instance
    except Exception as e:
        raise ValueError(e)


def get_total_amount(items):
    try:
        total_amount = 0
        for item in items:
            product = get_object_or_404(Product, id=item["product"])
            total_amount += item["quantity"] * product.price
        return total_amount
    except Exception as e:
        raise ValueError(e)

def activate_discount(discount_code, total_amount):
    try:
        discount = get_object_or_404(Discount, code=discount_code, is_active=True)
        if discount.discount_type == "percentage":
            total_amount *= (1 - (discount.value/100))
            print(total_amount)
        elif discount.discount_type == "fixed":
            total_amount = max(0, total_amount - discount.value)
            print(total_amount)
        return total_amount
    except Exception:
        return Response(
            {"message":"Invalid or expired discount code"}, status=400
        )

def activate_promotion(name, total_amount):
    try:
        promotion = get_object_or_404(Promotion, code=name, is_active=True)
        if promotion.discount.discount_type == "percentage":
            total_amount *= (1 - (promotion.discount.value/100))
        elif promotion.discount.discount_type == "fixed":
            total_amount = max(0, total_amount - promotion.disount.value)
        return total_amount
    except Exception:
        return Response(
            {"message":"Invalid or expired discount code"}, status=400
        )
