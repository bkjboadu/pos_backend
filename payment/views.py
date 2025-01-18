import stripe
from django.http import FileResponse
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.utils import generate_receipt_data, ReceiptGenerator
from django.shortcuts import get_object_or_404

from .models import Payment
from core.utils import (
    get_total_amount,
    activate_promotion,
    activate_discount,
    create_transaction,
)
from sales.models import Transaction, TransactionItem
from customers.models import Customer

# stripe payment setup
stripe.api_key = settings.STRIPE_SECRET_KEY


# process cash Payment
class PayCashView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            items = request.data["items"]
            customer_id = request.data.get('customer')
            customer = Customer.objects.get(id=customer_id) if customer_id else None
        except Exception:
            return Response("No items data provided", status=404)

        try:
            total_amount = get_total_amount(items)

            # check if there is discount
            discount_code = request.data.get("discount_code")
            promotion_name = request.data.get("promotion_name")
            if discount_code:
                total_amount = activate_discount(discount_code, total_amount)

            if promotion_name:
                total_amount = activate_promotion(promotion_name, total_amount)

            amount = request.data["amount"]
            if amount < total_amount:
                return Response(
                    {"message": "Cash less than total cost of goods"}, status=400
                )

            transaction_instance = create_transaction(items, total_amount, customer)
            Payment.objects.create(
                transaction=transaction_instance,
                payment_method="cash",
                total_amount=total_amount,
            )

            return Response(
                {
                    "message": "Payment Successful",
                    "balance": amount - total_amount,
                    "transaction": transaction_instance.id
                },
                status=200,
            )
        except Exception as e:
            return Response({"error": f"Payment Unsuccessful. {e}"}, status=400)


# split payment view
class SplitPaymentView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            items = request.data.get("items")
            cash_amount = request.data.get("cash_amount", 0)
            discount_code = request.data.get("discount_code")
            promotion_name = request.data.get("promotion_name")

            if not items:
                return Response({"error": "No items data provided"}, status=400)

            # Calculate total amount
            total_amount = get_total_amount(items)

            # Apply discount or promotion if available
            if discount_code:
                total_amount = activate_discount(discount_code, total_amount)

            if promotion_name:
                total_amount = activate_promotion(promotion_name, total_amount)

            if cash_amount > total_amount:
                return Response(
                    {"error": "Cash payment exceeds the total amount"}, status=400
                )

            remaining_balance = total_amount - cash_amount
            transaction_instance = create_transaction(items, total_amount)

            if cash_amount > 0:
                Payment.objects.create(
                    transaction=transaction_instance,
                    payment_method="Split",
                    amount=cash_amount,
                    stripe_charge_id=None,
                    stripe_status="Pending Card Payment"
                )

            # Handle Card Payment
            if remaining_balance > 0:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                intent = stripe.PaymentIntent.create(
                    amount = int(remaining_balance * 100),
                    currency='cad',
                    description=f"Payment for transaction #{transaction_instance.id}"
                )

                return Response(
                    {
                        "message": "Split payment initiated.",
                        "remaining_balance": remaining_balance,
                        "clientSecret": intent["client_secret"],
                        "payment_intent_id": intent["id"],
                        "transaction_id": transaction_instance.id,
                        "cash_amount": cash_amount
                    },
                    status=200,
                )

            return Response(
                {"message": "Payment completed fully with cash.", "transaction_id": transaction_instance.id},
                status=200,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ReceiptPDFView(APIView):
    '''
    Generates and serves a receipt PDF for a given transaction.
    '''
    def get(self, request, transaction_id):
        # Fetch the Transaction
        transaction = get_object_or_404(Transaction, id=transaction_id)

        receipt_data = generate_receipt_data(transaction)

        r = ReceiptGenerator()
        pdf_file_path = r.generate_small_receipt(receipt_data)

        # Serve the PDF file
        return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')


# process card payment
class StripePaymentIntentView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            items = request.data["items"]
        except Exception:
            return Response("No items data provided", status=404)

        try:
            total_amount = get_total_amount(items)

            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),
                currency="cad",
                payment_method_types=["card"],
            )
            return Response(
                {
                    "clientSecret": intent["client_secret"],
                    "payment_intent_id": intent["client_secret"].split("_secret_")[0],
                },
                status=200,
            )
        except Exception:
            return Response({"error": "Error creating Payment intent"}, status=400)


class StripePaymentConfirmView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        client_secret = request.data.get("clientSecret")
        items = request.data.get("items")
        cash_amount = request.data.get("cash_amount", 0)  # For split payments
        transaction_id = request.data.get("transaction_id")  # For split payments

        if not client_secret:
            return Response({"error": "Missing client secret"}, status=400)

        payment_intent_id = client_secret.split("_secret_")[0]

        try:
            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            stripe_charge_id = payment_intent.id
            stripe_intent_status = payment_intent.status
            amount_received = payment_intent.amount_received / 100  # Convert to dollars

            if stripe_intent_status == "succeeded":
                # Handle split payment scenario
                if transaction_id:
                    transaction_instance = Transaction.objects.get(id=transaction_id)

                    # Update the existing Payment record for split payments
                    payment = Payment.objects.get(
                        transaction=transaction_instance, payment_method="Split"
                    )
                    payment.total_amount += amount_received  # Add card payment to cash amount
                    payment.card_payment = amount_received
                    payment.stripe_charge_id = stripe_charge_id
                    payment.stripe_status = stripe_intent_status
                    payment.save()

                else:
                    # Handle full card payment scenario
                    transaction_instance = create_transaction(items)
                    Payment.objects.create(
                        transaction=transaction_instance,
                        stripe_charge_id=stripe_charge_id,
                        stripe_status=stripe_intent_status,
                        total_amount=amount_received,
                        card_payment=amount_received,
                        payment_method="card",
                    )

                return Response(
                    {
                        "status": "success",
                        "transaction": transaction_instance.id,
                        "message": "Your payment was successful!",
                    },
                    status=200,
                )

            return Response({"message": "Payment did not succeed"}, status=400)

        except stripe.error.StripeError as e:
            return Response({"message": str(e)}, status=400)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found for split"}, status=404)
