

from rest_framework.views import APIView
from rest_framework.response import Response
from sales.models import Transaction, TransactionItem
from sales.serializer import TransactionSerializer, TransactionItemSerializer
from payment.models import Payment
from payment.serializers import PaymentSerializer

class MetricsView(APIView):

    def get(self, request, *args, **kwargs):
        # Get query parameters
        query_params = request.query_params
        metric_type = query_params.get("metric", 'total_sales')
        start_date = query_params.get('start_date', now().data())
        end_date = query_params.get('end_date', now().date())
        product_id = query_params.get('product_id', None)

        # Filter transactions by date
        transactions = Transaction.objects.filter(
            created_at__date__gte=start_date, created_at__date__lte=end_date
        )

        # Handle different metrics types
        if metric_type == 'total_sales':
            total_sales = transactions.aggregate(total=Sum("total_amount"))["total"] or 0
            serialized_transactions = TransactionSerializer(transactions, many=True).data
            return Response({
                "metric": "total_sales",
                "value": total_sales,
                "transactions": serialized_transactions
            }, status=200)

        elif metric_type == "total_transactions":
            total_transactions = transactions.count()
            serialized_transactions = TransactionSerializer(transactions, many=True).data
            return Response({
                "metric": "total_transactions", "value": total_transactions, "transactions":serialized_transactions
            }, status=200)

        elif metric_type == "product_sales" and product_id:
            product_sales = (
                TransactionItem.objects.filter(
                    transaction_id=transactions, product_id=product_id
                )
                .aggregate(total=Sum("total_amount"))['total']
                or 0
            )

            # Serialize the list of transactions for the product
            filtered_transactions = transactions.filter(items__product_id=product_id).distint()
            serialized_transactions = TransactionSerializer(filtered_transactions, many=True).data
            return Response(
                {
                    "metric": "product_sales",
                    "product_id": product_id,
                    "value": product_sales,
                    "transactions": serialized_transactions,
                },
                status=200
            )

        elif metric_type == "top_products":
            top_products = (
                TransactionItem.objects.filter(transaction__in=transactions)
                .values("product__name")
                .annotate(total_sales=Sum("total_amount"), total_quantity=Sum("quantity"))
                .order_by("-total_sales")[:5]
            )
            # Extract product IDs to filter associated transactions
            product_ids = [product["product__id"] for product in top_products]

            # Filter transactions containing these products
            filtered_transactions = transactions.filter(items__product_id__in=product_ids).distinct()

            # Serialize the transactions
            serialized_transactions = TransactionSerializer(filtered_transactions, many=True).data

            return Response(
                {
                    "metric": "top_products",
                    "value": list(top_products),
                    "transactions": serialized_transactions,
                }
                , status=200
            )

        elif metric_type == "customer_sales":
            customer_sales = (
                transactions.values("customer__id", "customer__first_name", "customer__last_name")
                .annotate(total_sales=Sum("total_amount"))
                .order_by("-total_sales")
            )
            # Extract customer IDs to filter associated transactions
            customer_ids = [customer["customer__id"] for customer in customer_sales if customer["customer__id"] is not None]

            # Filter transactions related to the customers in the list
            filtered_transactions = transactions.filter(customer_id__in=customer_ids).distinct()

            # Serialize the transactions
            serialized_transactions = TransactionSerializer(filtered_transactions, many=True).data
            return Response(
                {
                    "metric": "customer_sales",
                    "value": list(customer_sales),
                    "transactions": serialized_transactions
                }, status=200)

        # Default response for unknown metrics
        return Response({"error": "Invalid metric or missing parameters"}, status=400)
