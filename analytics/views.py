from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Case, When, DecimalField, F
from sales.models import Transaction, TransactionItem
from sales.serializer import TransactionSerializer, TransactionItemSerializer
from inventory_management.models import Product
from payment.models import Payment
from datetime import datetime, timedelta

# Sales Analytics
class SalesByProductView(APIView):
    def get(self, request):
        # Get the product ID from query parameters
        product_id = request.query_params.get("product_id")

        # validate input
        if not product_id:
            return Response(
                {"error":"Product ID is required"},
                status=400
            )

        try:
            #
            transactions = Transaction.objects.filter(items__product_id=product_id)

            # Use the custom manager to get sales data.
            total_amount = Transaction.objects.sales_by_product(product_id=product_id)

            response_data = {
                "total_amount": total_amount,
                "transactions": list(transactions.values('id', 'created_at', 'total_amount', 'created_by', 'customer'))

            }
            return Response(response_data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SalesByDateView(APIView):
    def get(self, request):
        # get start and end date from query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # validate inputs
        if not start_date or not end_date:
            return Response(
                {"error":"Start and end date is required"},
                status=400
            )

        # Convert dates to datetime format
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0
            )
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0
            )

        except ValueError:
            return Response(
                {"error":"Invalid date format. Use YYYY-MM-DD"},
                status=400,
            )

        try:
            # Filter transactions
            transactions = Transaction.objects.filter(
                created_at__range=(start_datetime, end_datetime)
            )

            # Query sales data
            total_amount = Transaction.objects.total_sales(start_date=start_datetime, end_date=end_datetime)

            response_data = {
                "transactions": list(transactions.values('id', 'created_at', 'total_amount', 'created_by', 'customer')),
                "total_amount": total_amount
            }
            return Response(response_data, status=200)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=400)






class InventoryManagementAPIView(APIView):
    LOW_STOCK_THRESHOLD = 10  # Set the threshold as a constant

    def get(self, request):
        # Fetch low-stock items based on the threshold
        low_stock = Product.objects.filter(stock__lte=self.LOW_STOCK_THRESHOLD).values("name", "stock")

        # Fetch out-of-stock items
        out_of_stock = Product.objects.filter(stock=0).values("name")

        # Calculate stock valuation
        stock_valuation = Product.objects.aggregate(
            total_value=Sum(F("price") * F("stock"))
        )["total_value"] or 0


        return Response({
            "low_stock_alerts": list(low_stock),
            "out_of_stock_items": list(out_of_stock),
            "stock_valuation": stock_valuation,
        })


class PaymentRevenueInsightsAPIView(APIView):
    def get(self, request):
        # Payment Methods Breakdown
        total_payments = Payment.objects.count()
        payment_methods_breakdown = (
            Payment.objects.values("payment_method")
            .annotate(
                count=Count("id"),
                percentage=Case(
                    When(
                        payment_method__isnull=False,
                        then=(Count("id") * 100.0) / total_payments,
                    ),
                    output_field=DecimalField(max_digits=5, decimal_places=2),
                ),
            )
        )

        # Pending/Refunded Payments
        pending_payments = Payment.objects.filter(stripe_status="pending").aggregate(
            total_pending=Sum("amount")
        )["total_pending"] or 0

        refunded_payments = Payment.objects.filter(stripe_status="refunded").aggregate(
            total_refunded=Sum("amount")
        )["total_refunded"] or 0

        # Revenue Breakdown
        revenue_by_employee = (
            Payment.objects.values(employee=F("transaction__created_by__username"))
            .annotate(total_revenue=Sum("amount"))
            .order_by("-total_revenue")
        )

        revenue_by_location = (
            Payment.objects.values(location=F("transaction__customer__location"))
            .annotate(total_revenue=Sum("amount"))
            .order_by("-total_revenue")
        )

        revenue_by_channel = (
            Payment.objects.values(channel=F("transaction__created_by__channel"))
            .annotate(total_revenue=Sum("amount"))
            .order_by("-total_revenue")
        )

        return Response(
            {
                "payment_methods_breakdown": list(payment_methods_breakdown),
                "pending_payments": pending_payments,
                "refunded_payments": refunded_payments,
                "revenue_breakdown": {
                    "by_employee": list(revenue_by_employee),
                    "by_location": list(revenue_by_location),
                    "by_channel": list(revenue_by_channel),
                },
            }
        )
