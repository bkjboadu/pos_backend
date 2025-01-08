import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Payment
from inventory_management.models import Product
from sales.models import Transaction, TransactionItem


# stripe payment setup
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_transaction(items):
    # create transaction
    try:
        with transaction.atomic():
            transaction_instance = Transaction.objects.create()

            total_amount = 0
            for item in items:
                # get product instance
                product = get_object_or_404(Product, id=item["product"])
                total_amount += (item["quantity"] * product.price)
                TransactionItem.objects.create(
                    transaction=transaction_instance,
                    product=product,
                    quantity=item["quantity"],
                    total_amount=item["quantity"] * product.price
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
            total_amount += (item["quantity"] * product.price)
        return total_amount
    except Exception as e:
        raise ValueError(e)

# process cash Payment
class PayCash(APIView):
    def post(self, request, *args, **kwargs):
        try:
            items = request.data['items']
        except Exception:
            return Response("No items data provided",status=404)

        try:
            total_amount = get_total_amount(items)
            amount = request.data['amount']

            if amount < total_amount:
                return Response(
                    {
                        'message':'Cash less than total cost of goods'
                    },
                    status=400
                )

            transaction_instance = create_transaction(items)
            Payment.objects.create(
                transaction=transaction_instance,
                payment_method='cash',
                amount=total_amount,
            )

            return Response({
                'message':"Payment Successful",
                'balance': amount - total_amount
            },
            status=200)
        except Exception as e:
            return Response({"error":f"Payment Unsuccessful. {e}"}, status=400)

# process card payment
class StripePaymentIntentView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            items = request.data['items']
        except Exception:
            return Response("No items data provided",status=404)

        try:
            total_amount = get_total_amount(items)

            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),
                currency="cad",
                payment_method_types=["card"],
            )
            return Response({
                "clientSecret": intent["client_secret"],
                "payment_intent_id": intent['client_secret'].split('_secret_')[0]
            },
            status=200)
        except Exception:
            return Response({"error":"Error creating Payment intent"}, status=400)


class StripePaymentConfirmView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        client_secret = request.data.get('clientSecret')
        payment_intent_id = client_secret.split('_secret_')[0]
        items = request.data.get('items')
        print(request.data)

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            stripe_charge_id = payment_intent.id
            stripe_intent_status = payment_intent.status
            amount_received = payment_intent.amount_received / 100

            if stripe_intent_status == "succeeded":
                transaction_instance = create_transaction(items)


                Payment.objects.create(
                    transaction=transaction_instance,
                    stripe_charge_id=stripe_charge_id,
                    stripe_status=stripe_intent_status,
                    amount=amount_received,
                    payment_method='card'
                )
                return Response(
                    {
                        "status": "success",
                        "transaction": transaction_instance.id,
                        "message": "Your payment was successful!",
                    }
                )
            else:
                return Response(
                    {
                        "message":"Payment did not succeed"
                    },
                    status=400
                )

        except stripe.error.StripeError as e:
            return Response({"message": str(e)}, status=400)
